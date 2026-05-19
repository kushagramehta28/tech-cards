from bs4 import BeautifulSoup
import requests
from datetime import datetime


def scrape_arstechnica(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title = None
    og_title = soup.find("meta", property="og:title")

    if og_title:
        title = og_title.get("content")

    # Author
    author = None
    author_tag = soup.select_one(
        'div.font-impact a[href*="/author/"]'
    )
    if author_tag:
        author = author_tag.get_text(strip=True)

    # Date and Time
    dt = None

    published_meta = soup.find(
        "meta",
        property="article:published_time"
    )
    if published_meta:
        dt = datetime.fromisoformat(
            published_meta["content"]
        )

    # Image URL
    img_url = None
    og_image = soup.find(
        "meta",
        property="og:image"
    )
    if og_image:
        img_url = og_image.get("content")

    # Content
    content = ""
    article = soup.find("article")
    paragraphs = []

    if article:
        for p in article.find_all("p"):
            text = p.get_text(" ", strip=True)
            if not text:
                continue

            # skip junk
            if len(text) < 25:
                continue

            bad_words = [
                "Advertisement",
                "Read more",
                "Related Stories"
            ]

            if any(word in text for word in bad_words):
                continue

            paragraphs.append(text)

    content = "\n\n".join(paragraphs)

    return {
        "title": title,
        "author": author,
        "dt": dt,
        "image_url": img_url,
        "source": "Ars Technica",
        "article_url": url,
        "content": content
    }

# print(scrape_arstechnica("https://arstechnica.com/tech-policy/2026/05/iran-demands-big-tech-pay-fees-for-undersea-internet-cables-in-strait-of-hormuz/"))