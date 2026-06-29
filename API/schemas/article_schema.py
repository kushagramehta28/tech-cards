from pydantic import BaseModel
from datetime import datetime

class ArticleResponse(BaseModel):
    id: int
    title: str
    summary: str

    author: str | None

    source: str

    url: str

    image_url: str | None

    published_at: datetime | None

    isBookmarked: bool = False

    class Config:
        from_attributes = True
        # It allows Pydantic response models to convert SQLAlchemy ORM objects into API responses automatically