import requests
import trafilatura
import json
from datetime import datetime
from bs4 import BeautifulSoup
import cloudscraper


def scrape_bleepingcomputer(article_link):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Use cloudscraper to bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()
    response = scraper.get(article_link)

    extracted = trafilatura.extract(
        response.text,
        output_format="json",
        with_metadata=True
    )

    data = json.loads(extracted)

    # TITLE
    title = data.get("title")

    # AUTHOR
    author = data.get("author")

    # DATE + TIME
    raw_date = data.get("date")

    if raw_date:
        dt = datetime.fromisoformat(
            raw_date.replace("Z", "+00:00")
        )

    else:
        dt = "Unknown"

    # SOURCE
    source = "Bleeping Computer"

    # Beautiful Soup to extract image URL
    soup = BeautifulSoup(response.text, "lxml")

    # Find the centrally aligned image among all the images
    center_img = soup.select_one('p[style*="text-align:center"] img')

    if center_img:
        img_url = center_img.get("src")

    else:
        img_url = None

    # FULL ARTICLE CONTENT
    content = data.get("text")

    return {
        "title": title,
        "author": author,
        "dt": dt,
        "image_url": img_url,
        "source": source,
        "article_url": article_link,
        "content": content
    }

#scrape_bleepingcomputer("https://www.bleepingcomputer.com/news/microsoft/microsoft-confirms-patching-issues-in-restricted-windows-networks/")