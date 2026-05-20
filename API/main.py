from fastapi import FastAPI

from routes.auth import router as auth_router

from routes.articles import router as articles_router

from routes.bookmarks import router as bookmarks_router

app = FastAPI()

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(articles_router)

app.include_router(bookmarks_router)