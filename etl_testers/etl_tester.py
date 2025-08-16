import json
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data

def test_pipeline():
    """Test the full ETL pipeline locally"""
    try:
        print("🚀 Starting ETL pipeline test...")

        # Extract
        print("📥 Extracting data...")
        raw_data = extract_data()
        print(f"✅ Extracted {len(raw_data)} movies")

        # Transform
        print("🔄 Transforming data...")
        transformed_data = transform_data(raw_data)
        print(f"✅ Transformed {len(transformed_data.get('movies', []))} movies")

        # Load
        print("💾 Loading data into DB...")
        load_data(transformed_data)
        print("✅ Data successfully loaded into database")

        # Summary
        print(json.dumps({
            'message': 'ETL pipeline completed successfully',
            'movies_processed': len(transformed_data['movies'])
        }, indent=2))

    except Exception as e:
        print(f"❌ Error in ETL pipeline: {e}")

if __name__ == "__main__":
    test_pipeline()
