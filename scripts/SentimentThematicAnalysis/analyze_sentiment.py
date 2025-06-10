# analyze_sentiment.py

import os
import pandas as pd
import logging
from transformers import pipeline

# Set up logging
logging.basicConfig(
    filename="./../logs/analyze_sentiment.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_reviews(input_dir):
    """Load preprocessed review data for all banks."""
    reviews = []
    for bank in ['commercial bank of ethiopia reviews', 'Bank of Abyssinia reviews', 'Dashen bank reviews']:
        file_path = os.path.join(
            input_dir, f"{bank.lower().replace(' ', '_')}_clean.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['bank'] = bank
            reviews.append(df)
        else:
            logging.warning(f"File not found for {bank}: {file_path}")
    return pd.concat(reviews, ignore_index=True) if reviews else pd.DataFrame()


def analyze_sentiment(reviews_df):
    """Analyze sentiment using a pre-trained transformer model."""
    # Initialize sentiment analysis pipeline
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        top_k=None
    )

    # Process reviews in batches to manage memory
    batch_size = 32
    sentiments = []
    for i in range(0, len(reviews_df), batch_size):
        batch = reviews_df['review_text'].iloc[i:i +
                                               batch_size].fillna('').astype(str).tolist()
        results = sentiment_analyzer(batch)
        for j, result in enumerate(results):
            review_row = reviews_df.iloc[i + j]
            sentiments.append({
                'review_id': review_row.get('review_id', i + j),
                'review_text': batch[j],
                'sentiment_label': result[0]['label'],
                'sentiment_score': result[0]['score'],
                'bank': review_row.get('bank', 'Unknown'),
                'rating': review_row.get('rating'),
                'date': review_row.get('date') 
            })

        logging.info(f"Processed batch {i//batch_size + 1} of reviews")

    return pd.DataFrame(sentiments)


def aggregate_sentiment(sentiment_df):
    """Aggregate sentiment by bank and rating."""
    aggregated = sentiment_df.groupby(['bank', 'rating'])['sentiment_score'].agg([
        'mean', 'count']).reset_index()
    logging.info("Aggregated sentiment by bank and rating")
    return aggregated


def save_results(sentiment_df, output_dir):
    """Save sentiment analysis results for each bank separately."""
    # Group by bank and save individual files
    for bank in sentiment_df['bank'].unique():
        bank_df = sentiment_df[sentiment_df['bank'] == bank]
        file_name = f"sentiment_{bank.lower().replace(' ', '_')}.csv"
        bank_df.to_csv(os.path.join(output_dir, file_name), index=False)
        logging.info(f"Saved sentiment results for {bank} to {file_name}")


def sentiment():
    # Define directories
    input_dir = "./../data/processed"
    output_dir = "./../data/analyzed"
    os.makedirs(output_dir, exist_ok=True)

    # Load preprocessed reviews
    logging.info("Loading preprocessed reviews")
    reviews_df = load_reviews(input_dir)
    if reviews_df.empty:
        logging.error("No reviews loaded. Check input directory.")
        return

    # Analyze sentiment
    logging.info("Starting sentiment analysis")
    sentiment_df = analyze_sentiment(reviews_df)

    # Save results for each bank separately
    save_results(sentiment_df, output_dir)
    logging.info("Sentiment analysis completed successfully")
