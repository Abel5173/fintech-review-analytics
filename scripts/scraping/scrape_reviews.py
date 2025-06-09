import logging
import google_play_scraper as gp
from google_play_scraper import Sort
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
from typing import List, Dict
import os
import sys

project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(
    filename="./../logs/scrape_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define app IDs
app_ids = {
    'CBE': {'app_id': 'com.combanketh.mobilebanking', 'name': 'Commercial Bank of Ethiopia'},
    'BOA': {'app_id': 'com.boa.boaMobileBanking', 'name': 'Bank of Abyssinia'},
    'Dashen': {'app_id': 'com.dashen.dashensuperapp', 'name': 'Dashen Bank'}
}

# Define output directory
RAW_DATA_DIR = './../data/raw'
os.makedirs(RAW_DATA_DIR, exist_ok=True)


def scrape_bank_reviews(app_id: str, bank_name: str, target_clean_count: int = 400, min_raw_count: int = 600, max_reviews: int = 2000, lang: str = 'en', country: str = 'et') -> List[Dict]:
    logging.info(
        f"Starting to scrape up to {max_reviews} reviews for {bank_name} to achieve at least {min_raw_count} raw reviews for {target_clean_count} clean reviews")
    reviews = []
    continuation_token = None
    total_scraped = 0

    while total_scraped < max_reviews:
        try:
            result, new_token = gp.reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=100,
                continuation_token=continuation_token
            )

            if not result:
                logging.info(
                    f"No more reviews available for {bank_name} at {total_scraped} reviews. Maximum reached.")
                break

            for idx, review in enumerate(tqdm(result, desc=f"Processing {bank_name} reviews")):
                review_data = {
                    'review_id': f"{bank_name.replace(' ', '_')}_{total_scraped + idx}",
                    'review_text': review.get('content', ''),
                    'rating': review.get('score', None),
                    'date': review.get('at', None),
                    'bank_name': bank_name,
                    'source': 'Google Play'
                }
                reviews.append(review_data)

            total_scraped += len(result)
            logging.info(f"Scraped {total_scraped} reviews for {bank_name}")

            if not new_token:
                logging.info(
                    f"Continuation token exhausted for {bank_name} at {total_scraped} reviews. Maximum reached.")
                break
            continuation_token = new_token
            time.sleep(5)  # Increased delay to avoid rate limits

        except Exception as e:
            logging.warning(f"Error fetching reviews for {app_id}: {str(e)}")
            break

    if total_scraped < min_raw_count:
        logging.warning(
            f"Only {total_scraped} reviews scraped for {bank_name}, below minimum {min_raw_count}. Consider increasing max_reviews or checking API limits.")

    logging.info(
        f"Completed scraping {len(reviews)} reviews for {bank_name}. Estimated maximum reviews available.")
    return reviews

def save_to_csv(reviews: List[Dict], bank_name: str, output_dir: str) -> None:
    try:
        safe_bank_name = bank_name.replace(' ', '_').lower()
        output_path = os.path.join(output_dir, f"{safe_bank_name}_reviews.csv")
        df = pd.DataFrame(reviews)
        df.to_csv(output_path, index=False, encoding='utf-8')
        logging.info(f"Saved {len(df)} reviews to {output_path}")
    except Exception as e:
        logging.error(f"Error saving reviews for {bank_name} to CSV: {str(e)}")


def scrape():
    target_clean_reviews_per_bank = 400
    max_reviews_per_bank = 1000

    for bank, info in app_ids.items():
        # Scrape reviews for the current bank
        reviews = scrape_bank_reviews(
            app_id=info['app_id'],
            bank_name=info['name'],
            target_clean_count=target_clean_reviews_per_bank,
            max_reviews=max_reviews_per_bank
        )

        # Save to bank-specific CSV
        if reviews:
            save_to_csv(reviews, info['name'], RAW_DATA_DIR)

        # Log summary for the bank
        safe_bank_name = info['name'].replace(' ', '_').lower()
        output_path = os.path.join(
            RAW_DATA_DIR, f"{safe_bank_name}_reviews.csv")
        try:
            df = pd.read_csv(output_path)
            logging.info(f"Collected {len(df)} reviews for {info['name']}")
        except Exception as e:
            logging.error(f"Error reading CSV for {info['name']}: {str(e)}")

        time.sleep(2)  # Avoid rate limits between banks

    # Log total reviews across all banks
    total_reviews = 0
    for bank in app_ids.values():
        safe_bank_name = bank['name'].replace(' ', '_').lower()
        output_path = os.path.join(
            RAW_DATA_DIR, f"{safe_bank_name}_reviews.csv")
        try:
            df = pd.read_csv(output_path)
            total_reviews += len(df)
        except Exception as e:
            logging.error(f"Error reading CSV for {bank['name']}: {str(e)}")
    logging.info(f"Total reviews collected across all banks: {total_reviews}")


if __name__ == "__main__":
    scrape()
