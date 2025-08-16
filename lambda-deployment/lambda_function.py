import json
from extract import extract_data
from transform import transform_data
from load import load_data

def lambda_handler(event, context):
    '''AWS Lambda handler for ETL pipeline'''
    try:
        print("Starting ETL pipeline...")

        # Extract
        print("Extracting data...")
        raw_data = extract_data()
        print(f"✅ Extracted {len(raw_data)} movies")

        # Transform
        print("Transforming data...")
        transformed_data = transform_data(raw_data)
        print(f"✅ Transformed {len(transformed_data.get('movies', []))} movies")

        # Load
        print("Loading data...")
        load_data(transformed_data)
        print("✅ Data successfully loaded into database")

        return {
            'statusCode' : 200,
            'body' : json.dumps({
                'message' : 'ETL pipeline completed successfully',
                'movies_processed' : len(transformed_data['movies'])
            })
        }
    
    except Exception as e:
        print(f"Error in ETL pipeline: {e}")
        return {
            'statusCode' : 500,
            'body' : json.dumps({
                'error' : str(e)
            })
        }