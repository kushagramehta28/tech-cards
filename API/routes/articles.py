from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append("../database")

from database import engine
from models import Article

from schemas.article_schema import ArticleResponse

router = APIRouter()

Session = sessionmaker(bind=engine)

@router.get("/articles", response_model=list[ArticleResponse])
def get_articles():

    session = Session()

    try:
        # Get latest 50 articles ordered by published date in descending order
        articles = (
            session.query(Article)
            .order_by(Article.published_at.desc())
            .limit(50)
            .all()
        )

        return articles

    finally:
        session.close()

@router.get("/article/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int):
    session = Session()

    try:
        article = session.query(Article).filter_by(
            id=article_id
        ).first()

        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found"
            )

        return article

    finally:
        session.close()