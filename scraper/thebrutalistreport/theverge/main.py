import requests
import trafilatura
import json
from datetime import datetime
from bs4 import BeautifulSoup


def scrape_theverge(article_link):
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

    else:
        dt = None

    # SOURCE
    source = "The Verge"

    # Beautiful Soup to extract image URL
    soup = BeautifulSoup(response.text, "html.parser")

    # IMAGE
    # Grab the main article image container
    image_div = soup.find("div", class_="duet--layout--entry-image")
    img_url = None
    if image_div:
        img_tag = image_div.find("img")
        if img_tag:
            img_url = img_tag.get("src")

    # FULL ARTICLE CONTENT
    content = data.get("text")

    return {
        "title": title,
        "author": author,
        "dt" : dt,
        "image_url": img_url,
        "source": source,
        "article_url": article_link,
        "content": content
    }


#scrape_theverge("https://www.theverge.com/tech/928420/anker-solix-s2000-power-station")