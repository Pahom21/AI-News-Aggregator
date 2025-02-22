import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class NewsDatabase:
    def __init__(self, db_name="news.db"):
        """Initialize database connection and create table if it doesn't exist."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.create_table()
        self.add_sentiment_column()

    def create_table(self):
        """Creates the news table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,  -- Ensures no duplicate titles
            link TEXT UNIQUE,   -- Ensures no duplicate links
            content TEXT,
            source TEXT,
            category TEXT DEFAULT 'Uncategorized',
            sentiment TEXT DEFAULT 'NEUTRAL'
        );
        """
        try:
            self.conn.execute(query)
            self.conn.commit()
            logging.info("Database table initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error creating table: {e}")

    def add_sentiment_column(self):
        """Adds the sentiment column to the articles table if it doesn't exist."""
        cursor = self.conn.execute("PRAGMA table_info(articles);")
        columns = [row[1] for row in cursor.fetchall()]
        if "sentiment" not in columns:
            try:
                self.conn.execute("ALTER TABLE articles ADD COLUMN sentiment TEXT DEFAULT 'NEUTRAL';")
                self.conn.commit()
                logging.info("Sentiment column added successfully.")
            except sqlite3.Error as e:
                logging.error(f"Error adding sentiment column: {e}")
        else:
            logging.info("Sentiment column already exists.")

    def save_articles(self, articles):
        """Stores fetched articles in the database while preventing duplicates."""
        query = "INSERT OR IGNORE INTO articles (title, link, content, source, category, sentiment) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            with self.conn:
                self.conn.executemany(
                    query, [(a["title"], a["link"], a["content"], a["source"], a["category"], a["sentiment"]) for a in articles]
                )
            logging.info(f"Saved {len(articles)} articles to the database.")
        except sqlite3.Error as e:
            logging.error(f"Error saving articles: {e}")

    def get_filtered_articles(self, source=None, category=None, sentiment=None):
        """Fetch articles with optional filters."""
        query = "SELECT * FROM articles WHERE 1=1"
        params = []

        if source and source != 'all':
            query += " AND source = ?"
            params.append(source)
        if category and category != 'all':
            query += " AND category = ?"
            params.append(category)
        if sentiment and sentiment != 'all':
            query += " AND sentiment = ?"
            params.append(sentiment)

        try:
            cursor = self.conn.execute(query, params)
            rows = cursor.fetchall()

            # Convert rows (tuples) to dictionaries
            articles = []
            for row in rows:
                articles.append({
                    "id": row[0],
                    "title": row[1],
                    "link": row[2],
                    "content": row[3],
                    "source": row[4],
                    "category": row[5],
                    "sentiment": row[6]
                })

            return articles
        except sqlite3.Error as e:
            logging.error(f"Error fetching filtered articles: {e}")
            return []

    def fetch_all_articles(self):
        """Fetch all stored articles."""
        query = "SELECT * FROM articles"
        try:
            cursor = self.conn.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching articles: {e}")
            return []

    def fetch_articles_by_category(self, category):
        """Fetch articles based on a given category."""
        query = "SELECT * FROM articles WHERE category = ?"
        try:
            cursor = self.conn.execute(query, (category,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching articles by category: {e}")
            return []

    def update_category(self, title, category):
        """Updates the category of an article."""
        query = "UPDATE articles SET category = ? WHERE title = ?"
        try:
            with self.conn:
                self.conn.execute(query, (category, title))
            logging.info(f"Updated category for '{title}' to '{category}'.")
        except sqlite3.Error as e:
            logging.error(f"Error updating category: {e}")

    def delete_article(self, title):
        """Deletes an article based on the title."""
        query = "DELETE FROM articles WHERE title = ?"
        try:
            with self.conn:
                self.conn.execute(query, (title,))
            logging.info(f"Deleted article: {title}")
        except sqlite3.Error as e:
            logging.error(f"Error deleting article: {e}")

    def clear_articles(self):
        """Clears all articles from the database."""
        try:
            self.conn.execute("DELETE FROM articles")
            self.conn.commit()
            logging.info("Cleared all articles from the database.")
        except sqlite3.Error as e:
            logging.error(f"Error clearing articles: {e}")

    def close_connection(self):
        """Closes the database connection."""
        self.conn.close()
        logging.info("Database connection closed.")

# Example usage
if __name__ == "__main__":
    db = NewsDatabase()
    # Example: Fetch all articles
    articles = db.fetch_all_articles()
    for article in articles:
        print(article)

    # Close connection when done
    db.close_connection()
