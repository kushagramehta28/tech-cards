from pydantic import BaseModel

class BookmarkResponse(BaseModel):
    article_id: int
    title: str
    content : str