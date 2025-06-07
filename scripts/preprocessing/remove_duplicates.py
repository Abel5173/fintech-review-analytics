import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    filename="./../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def remove_duplicates(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
    
    initial_len = len(df)
    df = df.drop_duplicates(subset=['review_text', 'date'], keep='first')
    logging.info(f"Removed {initial_len - len(df)} duplicates for {bank_name}. Remaining: {len(df)}")
    return df