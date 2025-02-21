import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DuplicateChecker:
    def __init__(self, threshold=0.8):
        """Initialize the duplicate checker with a similarity threshold."""
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def remove_duplicates(self, articles):
        """
        Removes duplicate articles based on cosine similarity.
        
        Args:
            articles (list of dict): List of articles with "title" and "content".
        
        Returns:
            list: Filtered articles with duplicates removed.
        """
        if not articles:
            return []

        texts = [article["content"] for article in articles]
        tfidf_matrix = self.vectorizer.fit_transform(texts)

        # Compute similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        to_remove = set()

        # Identify duplicates
        for i in range(len(articles)):
            for j in range(i + 1, len(articles)):
                if similarity_matrix[i, j] > self.threshold:
                    to_remove.add(j)

        # Keep only unique articles
        filtered_articles = [article for idx, article in enumerate(articles) if idx not in to_remove]
        
        logging.info(f"Removed {len(to_remove)} duplicate articles.")
        return filtered_articles

# Example usage
if __name__ == "__main__":
    articles = [
        {"title": "AI Breakthrough", "content": "AI has achieved a major breakthrough in 2024."},
        {"title": "AI Advancements", "content": "AI has achieved a major breakthrough in 2024."},  # Duplicate
        {"title": "New Tech Trends", "content": "Technology is evolving rapidly with new advancements."}
    ]

    checker = DuplicateChecker()
    unique_articles = checker.remove_duplicates(articles)

    for article in unique_articles:
        print(article)
