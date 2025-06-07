import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    filename="../../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def handle_missing_data(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
    
    initial_len = len(df)
    df = df.dropna(subset=['review_text', 'rating'])
    logging.info(f"Dropped {initial_len - len(df)} rows with missing review_text or rating for {bank_name}. Remaining: {len(df)}")
    return df