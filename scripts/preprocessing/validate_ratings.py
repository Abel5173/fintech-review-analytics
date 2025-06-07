import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    filename="../../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_ratings(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
    initial_len = len(df)
    df = df[df['rating'].isin([1, 2, 3, 4, 5])]
    logging.info(f"Filtered {initial_len - len(df)} invalid ratings for {bank_name}. Remaining: {len(df)}")
    return df