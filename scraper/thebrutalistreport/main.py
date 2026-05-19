from scrape_brutalist import scrape_brutalist_report
import modules

articles = scrape_brutalist_report()

for article in articles:
    result = modules.controller(article)

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

