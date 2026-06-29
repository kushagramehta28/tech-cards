from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import sessionmaker

import sys
sys.path.append("../database")

from database import engine
from models import Bookmark, Article, User

from auth_utils import get_current_user

from datetime import datetime, timezone

from schemas.bookmark_schema import BookmarkResponse

router = APIRouter()

Session = sessionmaker(bind=engine)

@router.post("/bookmark/{article_id}")
def bookmark_article(article_id: int, current_user: User = Depends(get_current_user)):
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

        existing_bookmark = session.query(Bookmark).filter_by(
            user_id=current_user.id,
            article_id=article_id
        ).first()

        if existing_bookmark:
            raise HTTPException(
                status_code=400,
                detail="Already bookmarked"
            )

        bookmark = Bookmark(
            user_id=current_user.id,
            article_id=article_id,
            created_at=datetime.now(timezone.utc)
        )

        session.add(bookmark)

        session.commit()

        return {
            "message": "Article bookmarked"
        }

    finally:
        session.close()

@router.get("/bookmarks", response_model=list[BookmarkResponse])
def get_bookmarks(current_user: User = Depends(get_current_user)):
    session = Session()

    try:
        bookmarks = (
            session.query(Bookmark, Article)
            .join(
                Article,
                Bookmark.article_id == Article.id
            )
            .filter(
                Bookmark.user_id == current_user.id
            )
            .all()
        )

        result = []

        for bookmark, article in bookmarks:

            result.append({
                "article_id": article.id,
                "title": article.title,
                "content": article.summary
            })

        return result

    finally:
        session.close()

@router.delete("/bookmark/{article_id}")
def delete_bookmark(article_id: int, current_user: User = Depends(get_current_user)):
    session = Session()

    try:
        bookmark = session.query(Bookmark).filter_by(
            user_id=current_user.id,
            article_id=article_id
        ).first()

        if not bookmark:
            raise HTTPException(
                status_code=404,
                detail="Bookmark not found"
            )

        session.delete(bookmark)
        session.commit()

        return {
            "message": "Bookmark deleted"
        }

    finally:
        session.close()