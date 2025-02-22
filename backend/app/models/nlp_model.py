from transformers import pipeline

# === CLASSIFICATION ===
# Load a pre-trained text classification model
classifier = pipeline('zero-shot-classification', model="facebook/bart-large-mnli")

CATEGORIES = ["Technology", "Sports", "Politics", "Business", "Health", "Entertainment"]

def categorize_article(article):
    """Classifies a news article into defined categories"""
    result = classifier(article, CATEGORIES)
    return result['labels'][0] # Return the top predicted category

# === SUMMARIZATION ===
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_article(article):
    """Summarizes a news article dynamically based on its length."""
    # Calculate max_length as 30% of the input length, but at least 50 tokens
    max_length = max(50, int(len(article.split()) * 0.3))
    min_length = max(20, int(len(article.split()) * 0.1))

    # Generate the summary dynamically
    summary = summarizer(article, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

# === Sentiment Analysis ===
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
def analyze_sentiment(article):
     """Analyzes the sentiment of a news article."""
     result = sentiment_analyzer(article)
     return result[0]['label']
