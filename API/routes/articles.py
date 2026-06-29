from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append("../database")

from database import engine
from models import Article, Bookmark, User
from auth_utils import (
    get_current_user,
    get_optional_user
)
from fastapi import Depends
from typing import Optional

from schemas.article_schema import ArticleResponse

router = APIRouter()

Session = sessionmaker(bind=engine)

current_user: Optional[User] = Depends(get_current_user)

@router.get("/articles", response_model=list[ArticleResponse])
def get_articles(
    offset: int = 0,
    limit: int = 50,
    current_user: User | None = Depends(get_optional_user)
):

    session = Session()

    try:

        articles = (
            session.query(Article)
            .order_by(Article.published_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []

        for article in articles:

            is_bookmarked = False

            if current_user:

                bookmark = session.query(Bookmark).filter_by(
                    user_id=current_user.id,
                    article_id=article.id
                ).first()

                is_bookmarked = bookmark is not None

            result.append({
                "id": article.id,
                "title": article.title,
                "author": article.author,
                "source": article.source,
                "summary": article.summary,
                "image_url": article.image_url,
                "url": article.url,
                "published_at": article.published_at,
                "isBookmarked": is_bookmarked
            })

        return result

    finally:
        session.close()

@router.get("/article/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    current_user: User | None = Depends(get_optional_user)
):

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

        is_bookmarked = False

        if current_user:

            bookmark = session.query(Bookmark).filter_by(
                user_id=current_user.id,
                article_id=article.id
            ).first()

            is_bookmarked = bookmark is not None

        return {
            "id": article.id,
            "title": article.title,
            "author": article.author,
            "source": article.source,
            "summary": article.summary,
            "image_url": article.image_url,
            "url": article.url,
            "published_at": article.published_at,
            "isBookmarked": is_bookmarked
        }

    finally:
        session.close()