import os
import pandas as pd
import oracledb
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")

# Path to the processed CSVs
THEMATIC_PATHS = {
    "CBE": "data/thematically_analyzed/commercial_bank_of_ethiopia_reviews_thematic_analysis.csv",
    "BOA": "data/thematically_analyzed/bank_of_abyssinia_reviews_thematic_analysis.csv",
    "Dashen": "data/thematically_analyzed/dashen_bank_reviews_thematic_analysis.csv"
}

SENTIMENT_PATHS = {
    "CBE": "data/analyzed/sentiment_commercial_bank_of_ethiopia_reviews.csv",
    "BOA": "data/analyzed/sentiment_bank_of_abyssinia_reviews.csv",
    "Dashen": "data/analyzed/sentiment_dashen_bank_reviews.csv"
}


def merge_data():
    merged_data = []
    for bank_code in THEMATIC_PATHS:
        theme_df = pd.read_csv(THEMATIC_PATHS[bank_code])
        senti_df = pd.read_csv(SENTIMENT_PATHS[bank_code])

        # Merge on review_text
        df = pd.merge(
            theme_df, senti_df[['review_text', 'sentiment_label',
                                'sentiment_score', 'rating', 'date']],
            on='review_text',
            how='inner'
        )
        df['bank'] = bank_code
        merged_data.append(df)

    df = pd.concat(merged_data, ignore_index=True)

    # Use rating_y and date_y as the canonical columns
    df = df.rename(columns={'rating_y': 'rating', 'date_y': 'date'})

    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Diagnose all relevant columns
    print("Sample data before cleaning:")
    print(df[['review_id', 'review_text', 'rating',
          'sentiment_score', 'date', 'bank']].head(10))
    print("\nData types:")
    print(df[['review_id', 'review_text', 'rating',
          'sentiment_score', 'date', 'bank']].dtypes)
    print("\nNull values:")
    print(df[['review_id', 'review_text', 'rating',
          'sentiment_score', 'date', 'bank']].isnull().sum())
    print("\nUnique values in rating:")
    print(df['rating'].unique())
    print("\nUnique values in sentiment_score:")
    print(df['sentiment_score'].unique())
    print("\nUnique values in review_text:")
    print(df['review_text'].unique()[:10])  # First 10 for brevity

    # Clean numeric columns
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['sentiment_score'] = pd.to_numeric(
        df['sentiment_score'], errors='coerce')

    # Clean text columns
    df['review_id'] = df['review_id'].astype(str).replace('nan', 'Unknown_ID')
    df['review_text'] = df['review_text'].astype(str).replace(
        'nan', 'No review text')  # Default for missing text
    df['sentiment_label'] = df['sentiment_label'].astype(
        str).replace('nan', 'Unknown')

    # Handle NaN for numeric columns
    # Adjust based on schema (e.g., 3 if non-nullable)
    df['rating'] = df['rating'].fillna(0)
    df['sentiment_score'] = df['sentiment_score'].fillna(
        0.5)  # Neutral value; adjust if needed

    print("\nSample data after cleaning:")
    print(df[['review_id', 'review_text', 'rating',
          'sentiment_score', 'date', 'bank']].head(10))

    # Optional: Skip rows with missing review_text if not desired
    # df = df[df['review_text'] != 'No review text']

    return df


def insert_data():
    df = merge_data()

    print("✅ Data merged:", df.shape)
    print("Columns in merged DataFrame:", df.columns.tolist())

    # Connect to Oracle
    conn = oracledb.connect(
        user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
    cursor = conn.cursor()

    # Check table schema for debugging
    cursor.execute(
        "SELECT column_name, data_type, nullable FROM user_tab_columns WHERE table_name = 'REVIEWS'")
    schema = cursor.fetchall()
    print("\nReviews table schema:")
    for column in schema:
        print(column)

    # Insert banks if not already there
    bank_names = {
        "CBE": "Commercial Bank of Ethiopia",
        "BOA": "Bank of Abyssinia",
        "Dashen": "Dashen Bank"
    }

    bank_id_map = {}
    for code, name in bank_names.items():
        cursor.execute(
            "MERGE INTO banks b USING (SELECT :name AS name FROM dual) d ON (b.name = d.name) "
            "WHEN NOT MATCHED THEN INSERT (name) VALUES (:name)",
            {"name": name}
        )
        conn.commit()
        cursor.execute(
            "SELECT id FROM banks WHERE name = :name", {"name": name})
        bank_id = cursor.fetchone()[0]
        bank_id_map[code] = bank_id

    # Insert reviews
    for index, row in df.iterrows():
        review_date = row['date']
        if pd.notnull(review_date) and hasattr(review_date, 'date'):
            review_date = review_date.date()
        elif pd.isnull(review_date):
            review_date = None

        # Convert NaN to None for all fields
        def safe_value(val):
            if pd.isnull(val):
                return None
            return val

        try:
            cursor.execute(
                """
                MERGE INTO reviews r
                USING (SELECT :review_id AS review_id FROM dual) d
                ON (r.review_id = d.review_id)
                WHEN NOT MATCHED THEN
                INSERT (
                    review_id, review_text, rating, review_date, bank_name, source, processed_text, identified_theme
                ) VALUES (
                    :review_id, :review_text, :rating, :review_date, :bank_name, :source, :processed_text, :identified_theme
                )
                """,
                {
                    "review_id": safe_value(row['review_id']),
                    "review_text": safe_value(row['review_text']),
                    "rating": float(row['rating']) if pd.notnull(row['rating']) else None,
                    "review_date": review_date,
                    "bank_name": safe_value(row['bank_name']),
                    "source": safe_value(row['source']),
                    "processed_text": safe_value(row['processed_text']),
                    "identified_theme": safe_value(row['identified_theme'])
                }
            )
        except oracledb.DatabaseError as e:
            print(f"Error inserting row {index}:")
            print(f"Row data: {row.to_dict()}")
            print(f"Error: {e}")
            raise

    conn.commit()
    cursor.close()
    conn.close()
    print("All reviews inserted.")


if __name__ == "__main__":
    insert_data()
    print("Starting data insertion...")
