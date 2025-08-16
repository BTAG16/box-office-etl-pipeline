import pandas as pd
from datetime import datetime

class MovieDataTransformer:
    def __init__(self):
        pass

    def transform_movies(self, raw_movies):
        '''Transform raw movie data for database storage'''
        transformed_movies = []

        for movie in raw_movies:
            transformed_movie = {
                'tmdb_id': movie.get('id'),
                'title': movie.get('title', ''),
                'release_date': movie.get('release_date'),
                'overview': movie.get('overview', ''),
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'original_language': movie.get('original_language'),
                'runtime': movie.get('runtime'),
                'budget': movie.get('budget', 0),
                'revenue': movie.get('revenue', 0)
            }

            # Handle empty release dates
            if not transformed_movie['release_date']:
                transformed_movie['release_date'] = None

            transformed_movies.append(transformed_movie)
        
        return transformed_movies

    def transform_genres(self, raw_movies):
        '''Extract and Transform genre data'''
        genres_set = set()

        for movie in raw_movies:
            if 'genres' in movie:
                for genre in movie['genres']:
                    genres_set.add((genre['id'], genre['name']))

        return [{'tmdb_genre_id' : g[0], 'name' : g[1]} for g in genres_set]
    
    def transform_daily_stats(self, raw_movies):
        '''Transform Daily statistics'''
        daily_stats = []
        current_date = datetime.now().date()

        for movie in raw_movies:
            stat = {
                'tmdb_movie_id': movie.get('id'),
                'date': current_date,
                'popularity': movie.get('popularity', 0),
                'vote_average': movie.get('vote_average', 0),
                'vote_count': movie.get('vote_count', 0)
            }
            daily_stats.append(stat)

        return daily_stats
    
    def extract_movie_genres(self, raw_movies):
        '''Extract movie-genre relationships'''
        movie_genres = []

        for movie in raw_movies:
            if 'genres' in movie:
                for genre in movie['genres']:
                    movie_genres.append({
                        'tmdb_movie_id': movie['id'],
                        'tmdb_genre_id': genre['id']
                    })

        return movie_genres
    

def transform_data(raw_data):
    '''Main transformaton function'''
    transformer = MovieDataTransformer()

    return {
        'movies' : transformer.transform_movies(raw_data),
        'genres' : transformer.transform_genres(raw_data),
        'daily_stats' : transformer.transform_daily_stats(raw_data),
        'movie_genres' : transformer.extract_movie_genres(raw_data)
    }