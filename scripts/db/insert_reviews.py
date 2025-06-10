import os
import pandas as pd
import oracledb
from dotenv import load_dotenv

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

    return pd.concat(merged_data, ignore_index=True)


def insert_data():
    df = merge_data()

    print("✅ Data merged:", df.shape)
    conn = oracledb.connect(
        user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
    cursor = conn.cursor()

    # Insert banks if not already there
    bank_names = {
        "CBE": "Commercial Bank of Ethiopia",
        "BOA": "Bank of Abyssinia",
        "Dashen": "Dashen Bank"
    }

    bank_id_map = {}

    for code, name in bank_names.items():
        cursor.execute(
            "MERGE INTO banks b USING (SELECT :1 AS name FROM dual) d ON (b.name = d.name) WHEN NOT MATCHED THEN INSERT (name) VALUES (:1)",
            [name]
        )
        conn.commit()
        cursor.execute("SELECT id FROM banks WHERE name = :1", [name])
        bank_id = cursor.fetchone()[0]
        bank_id_map[code] = bank_id

    # Insert reviews (assuming a reviews table exists with appropriate columns)
    for index, row in df.iterrows():
        cursor.execute(
            """
            MERGE INTO reviews r
            USING (SELECT :1 AS review_id, :2 AS review_text, :3 AS sentiment_label, :4 AS sentiment_score,
                          :5 AS rating, :6 AS date, :7 AS bank_id FROM dual) d
            ON (r.review_id = d.review_id)
            WHEN NOT MATCHED THEN
            INSERT (review_id, review_text, sentiment_label, sentiment_score, rating, date, bank_id)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
            """,
            [
                row['review_id'],
                row['review_text'],
                row['sentiment_label'],
                row['sentiment_score'],
                row['rating'],
                row['date'],
                bank_id_map[row['bank']]
            ]
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All reviews inserted.")


if __name__ == "__main__":
    insert_data()
    print("Starting data insertion...")
    