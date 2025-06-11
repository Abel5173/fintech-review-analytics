# README.md

# Fintech Review Analytics

This project provides a complete pipeline for scraping, preprocessing, analyzing, and visualizing user reviews of major Ethiopian fintech mobile banking apps from the Google Play Store. The workflow includes data collection, cleaning, quality assessment, sentiment analysis, thematic keyword extraction, and comprehensive reporting.

---

## Project Structure

```
.
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   ├── analyzed/
│   └── thematically_analyzed/
├── docs/
│   └── [visualizations: missing data, rating distributions, word clouds, etc.]
├── logs/
│   └── [log files for scraping and preprocessing]
├── notebooks/
│   ├── scrape_data.ipynb
│   └── preprocess_reviews.ipynb
└── scripts/
    ├── scraping/
    │   └── scrape_reviews.py
    ├── preprocessing/
    │   ├── preprocess_reviews.py
    │   ├── remove_duplicates.py
    │   ├── handle_missing_data.py
    │   ├── normalize_dates.py
    │   ├── validate_ratings.py
    │   └── visualize_data_quality.py
    └── SentimentThematicAnalysis/
        ├── analyze_sentiment.py
        └── keyword_extraction.py
```

---

## Workflow Overview

### 1. Data Collection

- **Script:** [`scripts/scraping/scrape_reviews.py`](scripts/scraping/scrape_reviews.py)
- **Description:** Scrapes user reviews for selected banking apps (Commercial Bank of Ethiopia, Bank of Abyssinia, Dashen Bank) from Google Play using `google_play_scraper`.
- **Output:** Raw CSV files in `data/raw/` (e.g., `commercial_bank_of_ethiopia_reviews.csv`).

### 2. Data Preprocessing

- **Notebook:** [`notebooks/preprocess_reviews.ipynb`](notebooks/preprocess_reviews.ipynb)
- **Scripts:** Modular preprocessing scripts in [`scripts/preprocessing/`](scripts/preprocessing/)
- **Steps:**
  - Remove duplicates based on `review_text` and `date`.
  - Handle missing data (drop rows with missing `review_text` or `rating`).
  - Normalize date formats to `YYYY-MM-DD`.
  - Validate ratings (ensure values are between 1 and 5).
  - Translate non-English/Amharic reviews to English.
  - Tokenize, lemmatize, and remove stopwords from review text.
- **Output:** Cleaned CSVs in `data/processed/` (e.g., `bank_of_abyssinia_reviews_clean.csv`).

### 3. Data Quality Assessment & Visualization

- **Script:** [`scripts/preprocessing/visualize_data_quality.py`](scripts/preprocessing/visualize_data_quality.py)
- **Description:** Generates visualizations for missing data percentages and rating distributions for each bank.
- **Output:** PNG plots in `docs/` (e.g., `boa_missing_data.png`, `boa_rating_distribution.png`).

### 4. Sentiment Analysis

- **Script:** [`scripts/SentimentThematicAnalysis/analyze_sentiment.py`](scripts/SentimentThematicAnalysis/analyze_sentiment.py)
- **Description:** Performs sentiment analysis on cleaned reviews and saves results per bank.
- **Output:** Sentiment-labeled CSVs in `data/analyzed/`.

### 5. Thematic Keyword Extraction

- **Script:** [`scripts/SentimentThematicAnalysis/keyword_extraction.py`](scripts/SentimentThematicAnalysis/keyword_extraction.py)
- **Description:** Extracts keywords, assigns themes to reviews, and saves thematic analysis results.
- **Output:** Thematic CSVs in `data/thematically_analyzed/`.

### 6. Reporting & Visualization

- **Directory:** [`docs/`](docs/)
- **Contents:** Visual summaries, including:
  - Missing data plots
  - Rating distribution plots
  - Word clouds for thematic keywords
  - Sentiment score summaries

---

## Example Data Schema

Each review (after preprocessing) contains:

| review_id                     | review_text                          | rating | date       | bank_name                   | source      |
| ----------------------------- | ------------------------------------ | ------ | ---------- | --------------------------- | ----------- |
| Commercial_Bank_of_Ethiopia_0 | "A great app. It's like carrying..." | 4      | 2025-06-07 | Commercial Bank of Ethiopia | Google Play |
| Bank_of_Abyssinia_1           | "Hello, I’m facing a problem..."     | 1      | 2025-06-03 | Bank of Abyssinia           | Google Play |
| Dashen_Bank_2                 | "love"                               | 3      | 2025-06-06 | Dashen Bank                 | Google Play |

---

## Outputs

- **Cleaned Reviews:** `data/processed/*_reviews_clean.csv`
- **Sentiment Analysis:** `data/analyzed/*_sentiment.csv`
- **Thematic Analysis:** `data/thematically_analyzed/*_thematic_analysis.csv`
- **Visualizations:** `docs/*_missing_data.png`, `docs/*_rating_distribution.png`, word clouds, etc.
- **Logs:** `logs/preprocess_reviews.log`, `logs/scrape_reviews.log`

---

## How to Run

### 1. Install Dependencies

```sh
pip install -r requirements.txt
```

### 2. Scrape Reviews

```sh
python scripts/scraping/scrape_reviews.py
```

### 3. Preprocess Reviews

Run the notebook [`notebooks/preprocess_reviews.ipynb`](notebooks/preprocess_reviews.ipynb) step by step, or use the modular scripts in [`scripts/preprocessing/`](scripts/preprocessing/).

### 4. Analyze Sentiment & Extract Keywords

```sh
python scripts/SentimentThematicAnalysis/analyze_sentiment.py
python scripts/SentimentThematicAnalysis/keyword_extraction.py
```

### 5. Review Outputs

- Check `data/processed/` for cleaned CSVs.
- Check `docs/` for visualizations.
- Check `logs/` for detailed logs.

---

## Data Quality Summary

- **Duplicates:** Removed based on `review_text` and `date`.
- **Missing Data:** <5% missing after cleaning.
- **Date Normalization:** All dates in `YYYY-MM-DD` format.
- **Rating Validation:** All ratings are integers between 1 and 5.
- **Visualizations:** Plots for missing data and rating distributions are available in `docs/`.

---

## Next Steps

- Verify cleaned CSVs in `data/processed/` for 400+ reviews per bank and <5% missing data.
- Review visualizations in `docs/`.
- Proceed to sentiment and thematic analysis using cleaned CSVs.
