import logging
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from langdetect import detect
from deep_translator import MyMemoryTranslator
import re

# Download required NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Set up logging
logging.basicConfig(
    filename="../../logs/preprocess_reviews.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Translator with a specific English target
translator = MyMemoryTranslator(target='en-US')


def is_amharic_text(text: str) -> bool:
    """Check if the text contains Amharic characters."""
    if not isinstance(text, str) or not text.strip():
        return False
    # Amharic Unicode range: U+1200 to U+137F
    amharic_pattern = re.compile(r'[\u1200-\u137F]')
    return bool(amharic_pattern.search(text))


def is_english_text(text: str) -> bool:
    """Check if the text is primarily English using langdetect."""
    try:
        return detect(text) == 'en'
    except:
        return False


def has_non_english_chars(text: str) -> bool:
    """Check for non-English characters (e.g., non-Latin, excluding Amharic for specific handling)."""
    if not isinstance(text, str) or not text.strip():
        return True
    english_chars = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?\'"-')
    # Exclude Amharic range for separate handling
    return any(ord(char) > 127 and not (0x1200 <= ord(char) <= 0x137F) or char not in english_chars for char in text)


def is_meaningful_text(text: str) -> bool:
    """Check if text contains meaningful content (excludes pure emojis or short noise)."""
    # Remove emojis and check length
    text_no_emojis = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    # Arbitrary threshold to avoid short noise
    return len(text_no_emojis.strip()) > 3


def translate_to_english(text: str) -> str:
    """Translate non-English or Amharic text to English with improved accuracy."""
    try:
        if not is_meaningful_text(text):
            return text  # Skip translation for emojis or short noise

        if is_amharic_text(text):
            logging.info(f"Translating Amharic text: {text[:50]}...")
            translated = translator.translate(text, source='am-ET')
        elif has_non_english_chars(text) and not is_english_text(text):
            logging.info(f"Translating non-English text: {text[:50]}...")
            translated = translator.translate(text)
        else:
            return text

        if translated and len(translated.strip()) > 0:
            logging.info(f"Translated text: {translated[:50]}...")
            return translated
        else:
            logging.warning(
                f"Translation failed or returned empty for: {text[:50]}...")
            return text
    except Exception as e:
        logging.error(f"Translation error for text {text[:50]}...: {e}")
        return text  # Fallback to original text


def preprocess_text(text: str) -> str:
    """Preprocess text: translate if needed, then tokenize and clean."""
    if not isinstance(text, str) or not text.strip():
        return ''

    # Translate if Amharic or non-English (excluding English-like text)
    if (is_amharic_text(text) or (has_non_english_chars(text) and not is_english_text(text))) and is_meaningful_text(text):
        logging.info(f"Translating text: {text[:50]}...")
        text = translate_to_english(text)
        logging.info(f"Translated text: {text[:50]}...")

    try:
        tokens = word_tokenize(text.lower())
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        tokens = [
            lemmatizer.lemmatize(word)
            for word in tokens
            if word.isalnum() and word not in stop_words
        ]
        return ' '.join(tokens) if tokens else ''
    except Exception as e:
        logging.error(f"Tokenization failed: {e}")
        return ''


