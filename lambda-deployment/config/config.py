import os
from dotenv import load_dotenv

load_dotenv()

#TMDB API
TMDB_API_KEY =os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

#AWS Configuration
S3_BUCKET = os.getenv("S3_BUCKET")

# Database Configuration
DB_CONFIG = {
    'host' : os.getenv('DB_HOST', 'localhost'),
    'database' : os.getenv('DB_NAME'),
    'user' : os.getenv('DB_USER'),
    'password' : os.getenv('DB_PASSWORD'),
    'port' : os.getenv('DB_PORT', '5432')
}