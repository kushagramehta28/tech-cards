from datetime import datetime
import sys
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append('../../CloudflareBypassForScraping-main')  # Go two levels up and then into the folder

from CloudflareBypasser import CloudflareBypasser 
from DrissionPage import ChromiumPage
from transformers import pipeline

# Set up the summarization pipeline globally to avoid reinitialization in the loop
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

def start_browser():
    # Initialize ChromiumPage
    driver = ChromiumPage()
    driver.get('http://www.morningbrew.com/tag/tech')

    # Bypass Cloudflare protection
    cf_bypasser = CloudflareBypasser(driver) 
    cf_bypasser.bypass()

    return driver 

def fetch_json(driver, url):
    # Fetch JSON data from the given URL using JavaScript execution in the browser context
    data = driver.run_js("""
        return fetch(arguments[0], {
            credentials: 'include'
        })
        .then(r => r.json())
    """, url)
    return data

def see_more(driver):
    # Find and click the 'See More' button by tag and text (5 times)
    for _ in range(5):
        # Try to find the 'See More' button and click it
        see_more_btn = driver.ele('tag:button@@text():See More')

        if see_more_btn:
            print('See More button found, clicking...')
            see_more_btn.click()
        else:
            print('See More button not found.')

def link_builder(driver):
    # Get HTML of home page
    html = driver.html

    # Extract build ID only
    build_match = re.search(
        r'/_next/static/([^/]+)/_ssgManifest\.js',
        html
    )

    if not build_match:
        print("Build ID not found")
        return []

    build_id = build_match.group(1)

    # Extract all story paths
    stories = re.findall(
        r'<a[^>]+href="(/stories/[^"]+)"',
        html
    )

    if not stories:
        print("Story paths not found")
        return []

    # Remove duplicates
    stories = list(set(stories))

    # Build final API URLs
    urls = []

    for story in stories:
        api_url = (
            f"https://www.morningbrew.com/_next/data/"
            f"{build_id}"
            f"{story}.json"
        )

        urls.append(api_url)

    return urls

def embedding_builder(text, content):
    # Create the embedding text
    embedding_text = f"""
        Title: {text}

        Content:
        {content}
    """

    model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    embedding = model.encode(
        embedding_text,
        normalize_embeddings=True # Normalize the embeddings to unit length so that cosine similarity can be used directly
    )

    return embedding


def json_parser(json_data):
    story = json_data["pageProps"]["storyData"]
    title = story["title"]
    author = story["authors"][0]["name"]
    
    # Raw ISO datestring from JSON
    raw_date = story["publishDate"]

    # Convert to datetime object
    dt = datetime.strptime(
        raw_date,
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )

    # Nicely formatted date and time
    date = dt.strftime("%B %d, %Y")
    time = dt.strftime("%I:%M %p")

    img_url = story["hero"]["image"]["asset"]["url"]
    source = "morningbrew"
    article_link = story["shareLinks"]["website"]

    print("Title:", title)
    print("Author:", author)
    print("Date:", date)
    print("Time:", time)
    print("Image URL:", img_url)
    print("Source:", source)
    print("Article URL:", article_link)

    # Parse article body
    content_blocks = story["content"]
    paragraphs = []
    for block in content_blocks:
        if "children" in block:
            text = "".join(
                child.get("text", "")
                for child in block["children"]
            )
            if text.strip():
                paragraphs.append(text)

    content = "\n\n".join(paragraphs)
    summary = summarize_text(content)
    print("Content Summary:", summary)

    # Get embedding for the article
    embedding = embedding_builder(title, content)
    print("Embedding:", embedding)

def browser_quit(driver):
    driver.quit()

def summarize_text(text):
    # Generate summary between 80 to 110 tokens ~ 60-80 words
    summary = summarizer(text, max_length=110, min_length=80, do_sample=False)
    return summary[0]['summary_text']