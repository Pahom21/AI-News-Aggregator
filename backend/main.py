from flask import Flask, render_template, request
from app.services.news_api_client import NewsAPIClient  # adjust import based on your actual function name
import logging


# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
news_client = NewsAPIClient()

@app.route('/')
def index():
    # Get filter value
    desired_source = request.args.get('source', 'all')
    desired_category = request.args.get('category', 'all')
    desired_sentiment = request.args.get('sentiment', 'all')

    # Log current filter state
    logging.info(f"Filters applied - Source: {desired_source}, Category: {desired_category}, Sentiment: {desired_sentiment}")

    try:
        # Get articles based on filters
        articles = news_client.get_articles(
            source=None if desired_source == 'all' else desired_source,
            category=None if desired_category == 'all' else desired_category,
            sentiment=None if desired_sentiment == 'all' else desired_sentiment
        )

        # Pass available filter options to the template for dynamic dropdowns if needed.
        available_sources = news_client.get_available_sources() or []
        available_categories = news_client.get_available_categories() or []
        available_sentiments = news_client.get_available_sentiments() or []

        # Log number of articles retrieved
        logging.info(f"Retrieved {len(articles)} articles")
    except Exception as e:
        logging.error(f"Error fetching articles: {e}")
        articles = []
        available_sources = []
        available_categories = []
        available_sentiments = []


    # Fetch the articles
    return render_template(
        'index.html',
        source = desired_source if desired_source else 'all',
        category = desired_category if desired_category else 'all',
        sentiment = desired_sentiment if desired_sentiment else 'all',
        articles=articles,
        available_sources=available_sources,
        available_categories=available_categories,
        available_sentiments=available_sentiments
    )

if __name__ == '__main__':
    app.run(debug=True)