import logging
import requests
from backend.app.config.database import NewsDatabase  # Import database
from backend.app.models.nlp_model import categorize_article, summarize_article, analyze_sentiment  # Import AI models

# Configure logging
logging.basicConfig(level=logging. INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class NewsAPIClient:
    API_KEY = "c086f5ef32fd4fe9b3830a78a0266281"  # Replace with your actual NewsAPI key
    BASE_URL = "https://newsapi.org/v2/top-headlines"

    def __init__(self):
        self.db = NewsDatabase()  # Initialize database connection

    def fetch_articles(self, sources, force_refresh=False):
        """
        Fetch news articles from NewsAPI and process them with AI.
        If force_refresh is False, return existing articles from DB.
        """
        if not force_refresh:
            # Check if we have articles in the database first
            existing_articles = self.db.get_filtered_articles()
            if existing_articles:
                logging.info("Returning existing articles from database")
                return existing_articles
        else:
            # Reinitialize the database by clearing old articles
            self.db.clear_articles()
        articles = []

        for source in sources:
            logging.info(f"Fetching news from {source} using NewsAPI...")
            params = {
                "sources": source,
                "apiKey": self.API_KEY,
                "pageSize": 5,  # Limit number of articles
                "language": "en"
            }

            try:
                response = requests.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                if "articles" in data:
                    for item in data["articles"]:
                        article_text = item["description"] or item["title"]  # Use description if available

                        # Process the article using AI models
                        category = categorize_article(article_text)
                        summary = summarize_article(article_text)
                        sentiment = analyze_sentiment(article_text)

                        # Store processed article
                        processed_article = {
                            "title": item["title"],
                            "link": item["url"],
                            "content": summary,  # Store the summarized content
                            "source": source,
                            "category": category,
                            "sentiment": sentiment
                        }
                        articles.append(processed_article)

            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch news from {source}: {e}")

        # Save processed articles to the database
        if articles:
            self.db.save_articles(articles)
            logging.info(f"Saved {len(articles)} processed articles to the database.")

        return articles

    def get_articles(self, source=None, category=None, sentiment=None):
        """Get filtered articles from the database."""
        articles = self.db.get_filtered_articles(source, category, sentiment)
        if not articles:
            logging.info("No articles found with current filters, fetching fresh articles")
            sources = [source] if source and source != 'all' else self.get_available_sources()
            articles = self.fetch_articles(sources, force_refresh=True)
        return articles

    def get_available_sources(self):
        """Get list of available news sources."""
        return ["bbc-news", "cnn", "al-jazeera-english"]

    def get_available_categories(self):
        """Get list of available categories."""
        return ["Technology", "Sports", "Politics", "Business",
                "Health", "Entertainment"]

    def get_available_sentiments(self):
        """Get list of available sentiment values."""
        return ["POSITIVE", "NEGATIVE", "NEUTRAL"]


# Example usage
if __name__ == "__main__":
    sources = ["bbc-news", "cnn", "al-jazeera-english"]  # Example sources

    client = NewsAPIClient()
    news_articles = client.fetch_articles(sources, force_refresh=True)

    print(f"Total articles fetched: {len(news_articles)}")
    for article in news_articles:
        print(article)

    # Now test filtering by a specific source, e.g., "cnn"
    filtered_articles = client.get_articles(source="cnn")
    print("\nFiltered Articles (source = cnn):")
    for article in filtered_articles:
        print(article)

    # Now test filtering by specific sentiment
    filtered_by_sentiment = client.get_articles(sentiment="NEGATIVE")
    print("\nFiltered Articles (sentiment = NEGATIVE):")
    for article in filtered_by_sentiment:
        print(article)
