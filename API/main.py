import sys
import os

# Add project root, API, and database directories to python path for production hosting
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "API"))
sys.path.append(os.path.join(base_dir, "database"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

from routes.auth import router as auth_router

from routes.articles import router as articles_router

from routes.bookmarks import router as bookmarks_router

# Scheduler for periodic cleanup of expired articles and self-pinging
from apscheduler.schedulers.background import BackgroundScheduler

from services.cleanup import (
    cleanup_expired_articles
)

def ping_self():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        try:
            response = requests.get(url, timeout=10)
            print(f"Keep-Alive ping: {url} -> Status {response.status_code}")
        except Exception as e:
            print(f"Keep-Alive ping failed: {e}")

scheduler = BackgroundScheduler()

scheduler.add_job(
    cleanup_expired_articles,
    "interval",
    hours=24
)

scheduler.add_job(
    ping_self,
    "interval",
    minutes=5
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

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Tech Cards API is running"}

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(articles_router)

app.include_router(bookmarks_router)