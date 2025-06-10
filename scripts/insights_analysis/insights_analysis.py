import pandas as pd


def compute_bank_comparison(df):
    comparison = df.groupby('bank').agg({
        'sentiment_score': 'mean',
        'rating': 'mean',
        'review_id': 'count'
    }).rename(columns={'review_id': 'review_count'}).reset_index()
    comparison['sentiment_score'] = comparison['sentiment_score'].round(3)
    comparison['rating'] = comparison['rating'].round(2)
    return comparison


def identify_drivers_pain_points(df):

    drivers_pain_points = {}
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]

        # Drivers: Top themes from positive sentiment reviews (rating >= 4)
        positive_df = bank_df[(bank_df['sentiment_label']
                               == 'positive') & (bank_df['rating'] >= 4)]
        drivers = positive_df['identified_theme'].value_counts().head(
            2).index.tolist()
        if not drivers:
            drivers = ['None identified']  # Fallback if no positive themes

        # Pain Points: Top themes from negative sentiment reviews (rating <= 2)
        negative_df = bank_df[(bank_df['sentiment_label']
                               == 'negative') & (bank_df['rating'] <= 2)]
        pain_points = negative_df['identified_theme'].value_counts().head(
            2).index.tolist()
        if not pain_points:
            pain_points = ['None identified']  # Fallback if no negative themes

        drivers_pain_points[bank] = {
            'drivers': drivers,
            'pain_points': pain_points
        }

    return drivers_pain_points
