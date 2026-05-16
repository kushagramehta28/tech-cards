from datetime import datetime, timedelta, timezone
import sys
import re
from sentence_transformers import SentenceTransformer

sys.path.append('../../database') # Add the database directory to the path to import database modules

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from database import engine
from models import Article

sys.path.append('../../CloudflareBypassForScraping-main')  # Go two levels up and then into the folder

from CloudflareBypasser import CloudflareBypasser 
from DrissionPage import ChromiumPage
from transformers import pipeline

# Set up the summarization pipeline globally to avoid reinitialization in the loop
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# Set up the sentence transformer model globally to avoid reinitialization in the loop
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Set up the database session to add article details to the database
Session = sessionmaker(bind=engine)

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

    embedding = embedding_model.encode(
        embedding_text,
        normalize_embeddings=True # Normalize the embeddings to unit length so that cosine similarity can be used directly
    )

    return embedding

def parse_metadata(json_data):
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

    return (title, author, dt, img_url, source, article_link, story) # Return story for further parsing in json_parser

def build_article_content_and_embedding(title, story):
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
    print("Embedding:", embedding[:10]) # Print the first 10 values of the embedding for ease of reading
    return (summary, embedding)

def controller(json_data):
    title, author, dt, img_url, source, article_link, story = parse_metadata(json_data)

    session = Session()
    try:
        if (url_exists(article_link, session)):
            return "url_duplicate"
        summary, embedding = build_article_content_and_embedding(title, story)
        result = semantic_check(embedding, session)
        if result == "semantic_duplicate":
            return "semantic_duplicate"
        add_article_to_db(title, summary, author, source, article_link, img_url, embedding, dt, session)
        return "inserted"
    finally:
        session.close()


def semantic_check(embedding, session):
    # Check cosine similarity with the most similar article in the database
    result = find_similar_article(embedding, session)
    if result:
        similar_article, distance = result # Unpack the result into the article and the distance

        similarity = 1 - distance # Convert cosine distance to similarity

        print("Most similar article:")
        print(similar_article.title)

        print("Similarity score:")
        print(similarity)

        if similarity > 0.92: # Threshold of 0.92 to determine whether the article is a semantic duplicate
            print("Semantic duplicate found. Skipping insert to db.")
            return "semantic_duplicate" 
        
        return "not_duplicate"


def add_article_to_db(title, summary, author, source, article_link, img_url, embedding, published_at, session):
    article = Article(
        title=title,
        summary=summary,
        author=author,
        source=source,
        url=article_link,
        image_url=img_url,
        embedding=embedding.tolist(), # tolist() because pgvector expects a list, not a numpy array
        published_at=published_at,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    session.add(article)
    session.commit()

    print ("Article inserted successfully.")
    return "inserted" # Return true if insertion is successful


def browser_quit(driver):
    driver.quit()


def summarize_text(text):
    # Generate summary between 80 to 110 tokens ~ 60-80 words
    summary = summarizer(text, max_length=110, min_length=80, do_sample=False)
    return summary[0]['summary_text']


def find_similar_article(embedding, session):
    # Find the most similar article in the database based on cosine similarity of embeddings

    result = session.execute(
        select(
            Article,
            Article.embedding.cosine_distance(
                embedding.tolist()
            ).label("distance")
        )
        .order_by("distance")
        .limit(1)
    ).first()

    # This selects all details of the article
    # Then, adds a column called "distance" which calculates the cosine distance between the embedding of the article being inserted and the embedding of each article in the database
    # Then, orders the results by distance (most similar first) 
    # and limits it to 1 result

    return result


def url_exists(article_url, session):
    # Check if an article with the same URL already exists in the database to prevent duplicates
    result = session.execute(
        select(Article).where(
            Article.url == article_url
        )
    ).first()

    return result is not None