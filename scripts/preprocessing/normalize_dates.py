import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    filename="../../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def normalize_dates(df: pd.DataFrame, bank_name: str) -> pd.DataFrame:
    """
    Normalize date column to YYYY-MM-DD format.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        bank_name (str): Name of the bank.
    
    Returns:
        pd.DataFrame: DataFrame with normalized dates.
    """
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        logging.info(f"Normalized dates for {bank_name}")
        missing_dates = df['date'].isnull().sum()
        if missing_dates > 0:
            logging.warning(f"{missing_dates} reviews for {bank_name} have invalid dates")
    except Exception as e:
        logging.error(f"Error normalizing dates for {bank_name}: {str(e)}")
    return df