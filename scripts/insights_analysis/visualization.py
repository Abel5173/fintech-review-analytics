import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
import os


def ensure_directory_exists(path):
    """Ensure the directory for saving plots exists."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def plot_sentiment_trends(df, save_path=None):
    """
    Plot sentiment trends over time for each bank.
    
    Args:
        df (pd.DataFrame): DataFrame with columns 'bank', 'date', 'sentiment_score'
        save_path (str, optional): Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    df['date'] = pd.to_datetime(df['date'])
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        bank_df.groupby('date')['sentiment_score'].mean().plot(label=bank)
    plt.title('Sentiment Trends Over Time by Bank')
    plt.xlabel('Date')
    plt.ylabel('Mean Sentiment Score')
    plt.legend()
    if save_path:
        ensure_directory_exists(save_path)
        plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return plt


def plot_rating_distribution(df, save_path=None):
    """
    Plot rating distribution for each bank.
    
    Args:
        df (pd.DataFrame): DataFrame with columns 'bank', 'rating'
        save_path (str, optional): Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='rating', hue='bank', multiple='stack', bins=5)
    plt.title('Rating Distribution by Bank')
    plt.xlabel('Rating (1-5)')
    plt.ylabel('Number of Reviews')
    if save_path:
        ensure_directory_exists(save_path)
        plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return plt


def plot_keyword_cloud(df, save_path=None):
    """
    Generate a word cloud of keywords/themes for all reviews.
    
    Args:
        df (pd.DataFrame): DataFrame with column 'identified_theme'
        save_path (str, optional): Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    text = ' '.join(df['identified_theme'].dropna().astype(str))
    if text.strip():  # Ensure there is text to generate the word cloud
        wordcloud = WordCloud(
            width=800, height=400, background_color='white', max_words=50).generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Keyword Cloud for Review Themes')
        if save_path:
            ensure_directory_exists(save_path)
            plt.savefig(save_path, bbox_inches='tight')
        plt.close()
    else:
        plt.text(0.5, 0.5, 'No themes available', ha='center', va='center')
        plt.axis('off')
        if save_path:
            ensure_directory_exists(save_path)
            plt.savefig(save_path, bbox_inches='tight')
        plt.close()
    return plt


def plot_sentiment_by_rating(df, save_path=None):
    """
    Plot average sentiment score by rating for each bank.
    
    Args:
        df (pd.DataFrame): DataFrame with columns 'bank', 'rating', 'sentiment_score'
        save_path (str, optional): Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='rating', y='sentiment_score', hue='bank')
    plt.title('Average Sentiment Score by Rating')
    plt.xlabel('Rating (1-5)')
    plt.ylabel('Mean Sentiment Score')
    if save_path:
        ensure_directory_exists(save_path)
        plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return plt


def plot_theme_distribution(df, save_path=None):
    """
    Plot distribution of themes per bank as a pie chart.
    
    Args:
        df (pd.DataFrame): DataFrame with columns 'bank', 'identified_theme'
        save_path (str, optional): Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    for bank in df['bank'].unique():
        plt.subplot(1, len(df['bank'].unique()), list(
            df['bank'].unique()).index(bank) + 1)
        theme_counts = df[df['bank'] ==
                          bank]['identified_theme'].value_counts().head(5)
        plt.pie(theme_counts, labels=theme_counts.index, autopct='%1.1f%%')
        plt.title(f'Theme Distribution: {bank}')
    plt.tight_layout()
    if save_path:
        ensure_directory_exists(save_path)
        plt.savefig(save_path, bbox_inches='tight')
    plt.close()
    return plt
