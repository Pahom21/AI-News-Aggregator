import requests
import logging
from bs4 import BeautifulSoup
from newspaper import Article
from ratelimit import limits, sleep_and_retry
from fake_useragent import UserAgent
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Rate limiting: 10 requests per minute
REQUESTS_PER_MINUTE = 10

class NewsScraper:
    def __init__(self, sources):
        """
        Initialize the NewsScraper with multiple sources.
        Each source should be a dictionary containing 'name', 'url', and 'article_selector'.
        """
        self.sources = sources
        self.user_agent = UserAgent()

    def get_headers(self):
        """Generates a User-Agent header for each request."""
        return {"User-Agent": self.user_agent.random}

    @sleep_and_retry
    @limits(calls=REQUESTS_PER_MINUTE, period=60)
    def fetch_html(self, url):
        """Fetch HTML content of the page with error handling."""
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {url}: {e}")
            return None

    def parse_articles(self, html, base_url, article_selector):
        """Extracts article titles and links from the HTML based on a given selector."""
        soup = BeautifulSoup(html, "lxml")
        articles = []

        for item in soup.select(article_selector):  # Use the dynamic selector
            title = item.get_text(strip=True)
            link = item.find("a")["href"] if item.find("a") else None
            if title and link:
                full_link = urljoin(base_url, link)
                articles.append({"title": title, "link": full_link})

        return articles

    def extract_full_text(self, article_url):
        """Uses Newspaper3k to fetch the full article text."""
        try:
            article = Article(article_url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            logging.warning(f"Newspaper3k failed for {article_url}, trying BeautifulSoup...")

            # Fallback using BeautifulSoup
            html = self.fetch_html(article_url)
            if html:
                soup = BeautifulSoup(html, "lxml")
                paragraphs = soup.find_all("p")
                return "\n".join(p.get_text(strip=True) for p in paragraphs)

            logging.error(f"Failed to extract article from {article_url}: {e}")
            return None

    def run(self):
        """Runs the scraping process for all sources."""
        all_articles = []
        for source in self.sources:
            logging.info(f"Scraping: {source['name']} ({source['url']})")
            html = self.fetch_html(source["url"])
            if html:
                articles = self.parse_articles(html, source["url"], source["article_selector"])
                for article in articles:
                    logging.info(f"Fetching content for: {article['title']}")
                    article["content"] = self.extract_full_text(article["link"])
                    article["source"] = source["name"]
                all_articles.extend(articles)

        return all_articles

# Example Usage
if __name__ == "__main__":
    sources = [
        {"name": "Kenyans", "url": "https://www.kenyans.co.ke/", "article_selector": "h2"},
        {"name": "Citizen", "url": "https://citizen.digital/", "article_selector": "h3 a"},  # Example
        # Add more sources here
    ]

    scraper = NewsScraper(sources)
    news_articles = scraper.run()

    for article in news_articles:
        print(article)
