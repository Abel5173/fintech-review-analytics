import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from collections import defaultdict
import logging
import sys

# Ensure the logs directory exists
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')
os.makedirs(log_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=os.path.join(log_dir, "keyword_extraction.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Check and download spaCy model if not present
try:
    nlp = spacy.load("en_core_web_sm")
    logging.info("spaCy model 'en_core_web_sm' loaded successfully")
except OSError:
    logging.warning("spaCy model 'en_core_web_sm' not found. Downloading...")
    os.system(f"{sys.executable} -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    logging.info("spaCy model 'en_core_web_sm' downloaded and loaded")


def preprocess_text(text: str) -> str:
    """Preprocess text with spaCy: tokenize, lemmatize, remove stop words."""
    if not isinstance(text, str) or not text.strip():
        return ""
    doc = nlp(text)
    return " ".join(token.lemma_ for token in doc if not token.is_stop and token.is_alpha)


def extract_keywords(reviews: pd.Series, top_n: int = 10) -> list:
    """Extract top keywords and n-grams using TF-IDF."""
    tfidf = TfidfVectorizer(
        max_features=1000, ngram_range=(1, 2), stop_words='english')
    tfidf_matrix = tfidf.fit_transform(reviews)
    feature_names = tfidf.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().sum(axis=0)
    keyword_scores = dict(zip(feature_names, tfidf_scores))
    return sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]


def assign_themes(keywords: list, bank_name: str) -> dict:
    """Manually cluster keywords into 3-5 themes based on bank-specific logic."""
    themes = defaultdict(list)

    if "commercial bank of ethiopia" in bank_name.lower():
        themes['Account Access Issues'].extend(
            [k for k, _ in keywords if any(x in k for x in ['login', 'access', 'error'])])
        themes['Transaction Performance'].extend(
            [k for k, _ in keywords if any(x in k for x in ['transfer', 'slow', 'crash'])])
        themes['User Interface & Experience'].extend(
            [k for k, _ in keywords if any(x in k for x in ['ui', 'interface', 'easy'])])
        themes['Customer Support'].extend([k for k, _ in keywords if any(
            x in k for x in ['support', 'help', 'service'])])
        themes['Feature Requests'].extend(
            [k for k, _ in keywords if any(x in k for x in ['feature', 'update', 'add'])])

    elif "bank of abyssinia" in bank_name.lower():
        themes['Transaction Performance'].extend(
            [k for k, _ in keywords if any(x in k for x in ['transfer', 'delay', 'fail'])])
        themes['Account Access Issues'].extend(
            [k for k, _ in keywords if any(x in k for x in ['login', 'password', 'issue'])])
        themes['User Interface & Experience'].extend([k for k, _ in keywords if any(
            x in k for x in ['design', 'navigation', 'simple'])])
        themes['Customer Support'].extend([k for k, _ in keywords if any(
            x in k for x in ['contact', 'assistance', 'team'])])

    elif "dashen bank" in bank_name.lower():
        themes['User Interface & Experience'].extend(
            [k for k, _ in keywords if any(x in k for x in ['layout', 'smooth', 'app'])])
        themes['Transaction Performance'].extend(
            [k for k, _ in keywords if any(x in k for x in ['payment', 'slow', 'process'])])
        themes['Account Access Issues'].extend(
            [k for k, _ in keywords if any(x in k for x in ['sign', 'lock', 'problem'])])
        themes['Feature Requests'].extend(
            [k for k, _ in keywords if any(x in k for x in ['new', 'option', 'improve'])])

    # Remove duplicates and empty themes
    for theme in list(themes.keys()):
        themes[theme] = list(dict.fromkeys(themes[theme]))
        if not themes[theme]:
            del themes[theme]

    logging.info(f"Assigned themes for {bank_name}: {list(themes.keys())}")
    return themes


def process_bank_reviews(input_dir: str, output_dir: str, bank_name: str):
    """Process reviews for a single bank, extract keywords, assign themes, and save."""
    safe_bank_name = bank_name.replace(' ', '_').lower()
    input_path = os.path.join(input_dir, f"{safe_bank_name}_clean.csv")

    if not os.path.exists(input_path):
        logging.error(f"Input file not found for {bank_name}: {input_path}")
        return

    # Load data
    df = pd.read_csv(input_path)
    logging.info(f"Loaded {len(df)} cleaned reviews for {bank_name}")

    # Preprocess text
    df['processed_text'] = df['review_text'].apply(preprocess_text)

    # Extract keywords
    keywords = extract_keywords(df['processed_text'].dropna())
    logging.info(f"Extracted top keywords for {bank_name}: {keywords}")

    # Assign themes
    themes = assign_themes(keywords, bank_name)

    # Map themes to reviews (simplified rule-based assignment)
    def assign_review_theme(row):
        text = row['processed_text'].lower()
        for theme, theme_keywords in themes.items():
            if any(keyword in text for keyword in theme_keywords):
                return theme
        return 'Other'

    df['identified_theme'] = df.apply(assign_review_theme, axis=1)

    # Save results
    output_path = os.path.join(
        output_dir, f"{safe_bank_name}_thematic_analysis.csv")
    df.to_csv(output_path, index=False, encoding='utf-8')
    logging.info(f"Saved thematic analysis for {bank_name} to {output_path}")


def thematic():
    input_dir = "./../data/processed"
    output_dir = "./../data/thematically_analyzed"
    os.makedirs(output_dir, exist_ok=True)

    banks = ['commercial bank of ethiopia reviews',
             'bank of abyssinia reviews', 'dashen bank reviews']

    for bank in banks:
        process_bank_reviews(input_dir, output_dir, bank)


