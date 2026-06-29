from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router

from routes.articles import router as articles_router

from routes.bookmarks import router as bookmarks_router

# Scheduler for periodic cleanup of expired articles
from apscheduler.schedulers.background import BackgroundScheduler

from services.cleanup import (
    cleanup_expired_articles
)

scheduler = BackgroundScheduler()

scheduler.add_job(
    cleanup_expired_articles,
    "interval",
    hours=24
)

scheduler.start()

# API Logic starts here
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(articles_router)

app.include_router(bookmarks_router)