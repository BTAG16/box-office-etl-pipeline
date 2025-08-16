import requests
import json 
import boto3
from datetime import datetime
from config.config import TMDB_API_KEY, TMDB_BASE_URL, S3_BUCKET

class MovieDataExtractor:
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.s3_client = boto3.client('s3')

    def get_popular_movies(self, pages=1):
        '''Fetch popular movies from TMDB API'''
        all_movies = []

        for page in range(1, pages + 1):
            url = f"{self.base_url}/movie/popular"
            params = {
                'api_key' : self.api_key,
                'page' : page,
                'language' : 'en-US'
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                all_movies.extend(data['results'])
            else:
                print(f"Error fetching page {page}: {response.status_code}")

        return all_movies

    def get_movie_details(self, movie_id):
        '''Get detailed movie information'''
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key' : self.api_key,
            'language' : 'en-US'
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def save_raw_data_to_s3(self, data, filename):
        '''Save raw JSON data to S3'''
        try:
            self.s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=f"raw-data/{filename}",
                Body=json.dumps(data, indent=2),
                ContentType='application/json'
            )
            print(f"Saved {filename} to S3")
            return True
        except Exception as e:
            print(f"Error saving to S3: {e}")
            return False
        
def extract_data():
    '''Main Extraction Function'''
    extractor = MovieDataExtractor()

    # Get popular movies
    popular_movies = extractor.get_popular_movies(pages=3)

    # Get detailed info for top movies
    detailed_movies = []
    for movie in popular_movies[:5]:
        details = extractor.get_movie_details(movie['id'])
        if details:
            detailed_movies.append(details)

    # Save t0 S3
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extractor.save_raw_data_to_s3(
        detailed_movies,
        f"movies_detailed_{timestamp}.json"
    )

    return detailed_movies