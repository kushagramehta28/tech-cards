import requests
import trafilatura
import json
from datetime import datetime
from bs4 import BeautifulSoup


def scrape_phoronix(article_link):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(article_link, headers=headers)

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

        date = dt.strftime("%B %d, %Y")
        time = dt.strftime("%I:%M %p")

    else:
        date = "Unknown"
        time = "Unknown"

    # SOURCE
    source = "phoronix"

    # Beautiful Soup to extract image URL
    soup = BeautifulSoup(response.text, "lxml")

    # Find the centrally aligned image among all the images
    center_img = soup.select_one('p[align="center"] img')

    if center_img:
        img_url = center_img.get("src")

        # Fix protocol-relative URLs
        if img_url.startswith("//"):
            img_url = "https:" + img_url
    else:
        img_url = None

    # FULL ARTICLE CONTENT
    content = data.get("text")

    return {
        "title": title,
        "author": author,
        "date": date,
        "time": time,
        "image_url": img_url,
        "source": source,
        "article_url": article_link,
        "content": content
    }

scrape_phoronix(
    "https://www.phoronix.com/news/Intel-May-2026-OSS-Archived"
)