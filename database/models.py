from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

# Schema for users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    # Unique = true to prevent duplicate emails
    # nullable = false to ensure every user has an email and password
    email = Column(String, unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime)

# Schema for articles
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    summary = Column(Text, nullable=False)

    author = Column(String)

    source = Column(String, nullable=False)

    url = Column(String, unique=True, nullable=False)

    image_url = Column(String)

    embedding = Column(Vector(384))

    # index = true to allow for efficient querying based on publish date and expiration date
    published_at = Column(DateTime, index=True)

    created_at = Column(DateTime)

    expires_at = Column(DateTime, index=True)

# Schema for bookmarks
class Bookmark(Base):
    __tablename__ = "bookmarks"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True
    )

    article_id = Column(
        Integer,
        ForeignKey("articles.id"),
        primary_key=True
    )

    created_at = Column(DateTime)