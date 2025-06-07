import pandas as pd
import os
import logging
from typing import Optional

# logging
logging.basicConfig(
    filename="../../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_reviews(input_path: str, bank_name: str) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(input_path)
        logging.info(f"Loaded {len(df)} reviews for {bank_name} from {input_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading CSV for {bank_name}: {str(e)}")
        return None