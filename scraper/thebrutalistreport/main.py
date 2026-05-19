from scrape_brutalist import scrape_brutalist_report

from ArsTechnica.main import scrape_arstechnica
from theverge.main import scrape_theverge
from Phoronix.main import scrape_phoronix
from BleepingComputer.main import scrape_bleepingcomputer

SCRAPER_MAP = {
    "ArsTechnica": scrape_arstechnica,
    "The Verge": scrape_theverge,
    "Phoronix": scrape_phoronix,
    "Bleeping Computer": scrape_bleepingcomputer
}

articles = scrape_brutalist_report()

for article in articles:

    publisher = article["publisher"]
    url = article["url"]

    print("\n" + "=" * 80)
    print(f"SCRAPING: {publisher}")
    print(url)
    print("=" * 80)

    scraper_function = SCRAPER_MAP.get(publisher)

    if not scraper_function:
        print(f"No scraper found for {publisher}")
        continue

    try:
        scraped_data = scraper_function(url)
        print("\nSCRAPED SUCCESSFULLY")
        print(scraped_data)

    except Exception as e:
        print(f"Error scraping {url}")
        print(e)