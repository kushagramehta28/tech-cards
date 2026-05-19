from ArsTechnica.main import scrape_arstechnica
from theverge.main import scrape_theverge
from Phoronix.main import scrape_phoronix
from BleepingComputer.main import scrape_bleepingcomputer

from datetime import datetime, timedelta, timezone
import sys
from sentence_transformers import SentenceTransformer

sys.path.append('../../database') # Add the database directory to the path to import database modules

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from database import engine
from models import Article

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

# Map of publisher names to their respective scraping functions to use in the controller function
SCRAPER_MAP = {
    "ArsTechnica": scrape_arstechnica,
    "The Verge": scrape_theverge,
    "Phoronix": scrape_phoronix,
    "Bleeping Computer": scrape_bleepingcomputer
}

def url_exists(article_url, session):
    # Check if an article with the same URL already exists in the database to prevent duplicates
    result = session.execute(
        select(Article).where(
            Article.url == article_url
        )
    ).first()

    return result is not None

def summarize_text(text):
    # Generate summary between 80 to 110 tokens ~ 60-80 words
    summary = summarizer(text, max_length=110, min_length=80, do_sample=False)
    return summary[0]['summary_text']

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

        if similarity > 0.97: # Threshold of 0.97 to determine whether the article is a semantic duplicate
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

def build_summary_and_embedding(title, content):
    summary = summarize_text(content)

    # Get embedding for the article
    embedding = embedding_builder(title, content)

    return (summary, embedding)

def controller(article):
    publisher = article["publisher"]
    url = article["url"]

    scraper_function = SCRAPER_MAP.get(publisher)
    scraped_data = scraper_function(url)

    title = scraped_data['title']
    author = scraped_data['author']
    published_at = scraped_data['dt'] # This is the datetime object returned by the scrapers
    image_url = scraped_data['image_url']
    source = scraped_data['source']
    article_url = scraped_data['article_url']
    content = scraped_data['content']


    date = published_at.strftime("%B %d, %Y")
    time = published_at.strftime("%I:%M %p")

    session = Session()
    try:
        if (url_exists(article_url, session)):
            return "url_duplicate"
        summary, embedding = build_summary_and_embedding(title, content)
        result = semantic_check(embedding, session)
        if result == "semantic_duplicate":
            return "semantic_duplicate"
        print("Title:", title)
        print("Author:", author)
        print("Date:", date)
        print("Time:", time)
        print("Image URL:", image_url)
        print("Source:", source)
        print("Article URL:", article_url)
        print("\nSummary:\n", summary)  
        print("\nEmbedding (first 10 values):\n", embedding[:10], "...")
        
        add_article_to_db(title, summary, author, source, article_url, image_url, embedding, published_at, session)
        return "inserted"
    finally:
        session.close()