from .scrape_brutalist import scrape_brutalist_report
from . import modules

def main():
    articles = scrape_brutalist_report()

    for article in articles:
        result = modules.controller(article)

        # Skipping here because publishers are different, breaking could prevent new articles from other publishers being processed.
        if result == "url_duplicate":
            print(f"Duplicate article found for URL: {article['url']}")
            print("Skipping.")
            continue

        elif result == "semantic_duplicate":
            print(f"Semantic duplicate found for URL: {article['url']}")
            print("Skipping article.")
            continue

        elif result == "inserted":
            print(f"Article inserted for URL: {article['url']}")
            print("=" * 80)

