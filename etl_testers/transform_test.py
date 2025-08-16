# import boto3
# import json
# import pandas as pd
# from etl.transform import transform_data
# from config.config import S3_BUCKET

# # --- Config ---
# BUCKET_NAME = S3_BUCKET   # same as S3_BUCKET in config
# KEY = "{AWS_BUCKET_KEY}"  # replace with actual file key

# # --- Load raw data from S3 ---
# s3 = boto3.client("s3")
# response = s3.get_object(Bucket=BUCKET_NAME, Key=KEY)
# raw_data = json.loads(response["Body"].read().decode("utf-8"))

# # --- Run transformations ---
# transformed = transform_data(raw_data)

# # --- Inspect with Pandas ---
# movies_df = pd.DataFrame(transformed["movies"])
# genres_df = pd.DataFrame(transformed["genres"])
# stats_df = pd.DataFrame(transformed["daily_stats"])
# movie_genres_df = pd.DataFrame(transformed["movie_genres"])

# print("Movies:")
# print(movies_df.head())

# print("\nGenres:")
# print(genres_df.head())

# print("\nDaily Stats:")
# print(stats_df.head())

# print("\nMovie-Genre Relationships:")
# print(movie_genres_df.head())
