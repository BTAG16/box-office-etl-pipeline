import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from config.config import DB_CONFIG

class DatabaseLoader:
    def __init__(self):
        self.connection = None
        self.connect()
        pass

    def connect(self):
        '''Connect to PostgreSQL database'''
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            print("Database Connection successful")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def load_genres(self, genres_data):
        '''Load genres with upsert logic'''
        if not genres_data:
            return
        
        cursor = self.connection.cursor()

        # Upsert genres
        insert_query = """
            INSERT INTO genres (tmdb_genre_id, name)
            VALUES %s
            ON CONFLICT (tmdb_genre_id)
            DO UPDATE SET name = EXCLUDED.name
        """

        values = [(g['tmdb_genre_id'], g['name']) for g in genres_data]
        execute_values(cursor, insert_query, values)
        self.connection.commit()
        print(f"Loaded {len(genres_data)} genres")


    def load_movies(self, movies_data):
        '''Load movies with upsert logic'''
        if not movies_data:
            return

        cursor = self.connection.cursor()

        insert_query = """
            INSERT INTO movies (tmdb_id, title, release_date, overview, poster_path, 
                              backdrop_path, original_language, runtime, budget, revenue) 
            VALUES %s 
            ON CONFLICT (tmdb_id) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                release_date = EXCLUDED.release_date,
                overview = EXCLUDED.overview,
                poster_path = EXCLUDED.poster_path,
                backdrop_path = EXCLUDED.backdrop_path,
                original_language = EXCLUDED.original_language,
                runtime = EXCLUDED.runtime,
                budget = EXCLUDED.budget,
                revenue = EXCLUDED.revenue,
                updated_at = CURRENT_TIMESTAMP
        """

        values = [(
            m['tmdb_id'], m['title'], m['release_date'], m['overview'],
            m['poster_path'], m['backdrop_path'], m['original_language'],
            m['runtime'], m['budget'], m['revenue']
        ) for m in movies_data]
        execute_values(cursor, insert_query, values)
        self.connection.commit()
        print(f"Loaded {len(movies_data)} movies")


    def load_movie_genres(self, movie_genres_data):
        '''Load movie-genre relationships'''
        if not movie_genres_data:
            return
        
        cursor = self.connection.cursor()

        # First get movie and genre id's from database
        for mg in movie_genres_data:
            # Get movie ID 
            cursor.execute(
                "SELECT id FROM movies WHERE tmdb_id = %s",(mg['tmdb_movie_id'],)
            )
            movie_result = cursor.fetchone()

            # Get genre ID
            cursor.execute(
                "SELECT id FROM genres WHERE tmdb_genre_id = %s",(mg['tmdb_genre_id'],)
            )
            genre_result = cursor.fetchone()

            if movie_result and genre_result:
                # Insert relationship
                cursor.execute(
                    """INSERT INTO movie_genres (movie_id, genre_id)
                       VALUES (%s, %s)
                       ON CONFLICT (movie_id, genre_id) DO NOTHING""",
                       (movie_result[0], genre_result[0])
                )
            
        self.connection.commit()
        print(f"Loaded movie-genre relationships")


    def load_daily_stats(self, stats_data):
        '''Load daily stats'''
        if not stats_data:
            return
        
        cursor = self.connection.cursor()

        for stat in stats_data:
            # Get movie ID
            cursor.execute(
                "SELECT id FROM movies WHERE tmdb_id = %s", (stat['tmdb_movie_id'],)
            )
            movie_result = cursor.fetchone()

            if movie_result:
                cursor.execute(
                    """INSERT INTO daily_stats (movie_id, date, popularity, vote_average, vote_count) 
                       VALUES (%s, %s, %s, %s, %s) 
                       ON CONFLICT (movie_id, date) 
                       DO UPDATE SET 
                           popularity = EXCLUDED.popularity,
                           vote_average = EXCLUDED.vote_average,
                           vote_count = EXCLUDED.vote_count""",
                    (movie_result[0], stat['date'], stat['popularity'], 
                     stat['vote_average'], stat['vote_count'])
                )

        self.connection.commit()
        print(f"Loaded {len(stats_data)} daily stats")

    
    def close(self):
        '''Close database connection'''
        if self.connection:
            self.connection.close()

def load_data(transformed_data):
    '''Main loading function'''
    loader = DatabaseLoader()

    try:
        # Load in correct order due to foreign key dependencies
        loader.load_genres(transformed_data['genres'])
        loader.load_movies(transformed_data['movies'])
        loader.load_movie_genres(transformed_data['movie_genres'])
        loader.load_daily_stats(transformed_data['daily_stats'])

    finally:
        loader.close()