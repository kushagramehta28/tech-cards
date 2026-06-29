from sqlalchemy.orm import sessionmaker

from database import engine
from models import Article, Bookmark

from datetime import datetime, timezone

Session = sessionmaker(bind=engine)

def cleanup_expired_articles():

    session = Session()

    try:

        now = datetime.now(timezone.utc)

        expired_unbookmarked_articles = (
            session.query(Article)
            .outerjoin(
                Bookmark,
                Bookmark.article_id == Article.id
            )
            .filter(
                Article.expires_at < now,
                Bookmark.id == None
            )
            .all()
        )

        deleted_count = len(
            expired_unbookmarked_articles
        )

        for article in expired_unbookmarked_articles:

            print(
                f"Deleting article -> "
                f"ID: {article.id}, "
                f"Title: {article.title}"
            )

            session.delete(article)

        session.commit()

        print(
            f"Deleted {deleted_count} expired articles"
        )

    except Exception as error:

        session.rollback()

        print(error)

    finally:

        session.close()