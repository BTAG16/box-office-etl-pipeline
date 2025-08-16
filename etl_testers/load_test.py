# Test Code for Load

from etl.load import DatabaseLoader  # adjust if DatabaseLoader is elsewhere

def main():
    loader = None
    try:
        # Initialize DB connection
        loader = DatabaseLoader()
        print("✅ Database connection successful")

        # Test insert into genres table
        test_genre = {"tmdb_genre_id": 9999, "name": "Test Genre"}
        print("🚀 Inserting test row...")

        loader.load_genres([test_genre])  # uses your upsert logic

        # Verify insert
        with loader.connection.cursor() as cur:
            cur.execute("SELECT name FROM genres WHERE tmdb_genre_id = %s", (9999,))
            result = cur.fetchone()
            if result and result[0] == "Test Genre":
                print("✅ Insert verified successfully")
            else:
                print("❌ Insert verification failed")

        # Clean up test row
        with loader.connection.cursor() as cur:
            cur.execute("DELETE FROM genres WHERE tmdb_genre_id = %s", (9999,))
        loader.connection.commit()
        print("🧹 Test row deleted successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if loader and loader.connection:
            loader.connection.close()
            print("🔒 Database connection closed")

if __name__ == "__main__":
    main()
