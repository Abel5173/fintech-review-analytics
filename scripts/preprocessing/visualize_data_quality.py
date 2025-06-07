import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

# logging
logging.basicConfig(
    filename="../../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def visualize_data_quality(df: pd.DataFrame, bank_name: str, output_dir: str) -> None:
    safe_bank_name = bank_name.replace(' ', '_').lower()

    # Plot missing data
    plt.figure(figsize=(8, 5))
    missing = df.isnull().mean() * 100
    missing.plot(kind='bar', color='#1f77b4')
    plt.title(f'Missing Data Percentage for {bank_name}')
    plt.ylabel('Percentage Missing (%)')
    plt.xlabel('Columns')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{safe_bank_name}_missing_data.png'))
    plt.close()

    plt.show()

    # Plot rating distribution
    plt.figure(figsize=(8, 5))
    sns.countplot(x='rating', data=df, color='#1f77b4')
    plt.title(f'Rating Distribution for {bank_name}')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(
        output_dir, f'{safe_bank_name}_rating_distribution.png'))
    plt.show()
    plt.close()
    logging.info(
        f"Saved data quality visualizations for {bank_name} to {output_dir}")
