from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from fastapi import Depends
from typing import Optional
optional_oauth2_scheme = HTTPBearer(auto_error=False)
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append("../database")
from database import engine
from models import User

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"], # Use bcrypt algorithm for hashing passwords
    deprecated="auto"
)

def get_optional_user(
    token = Depends(optional_oauth2_scheme)
):
    if not token:
        return None
    try:
        return get_current_user(
            token.credentials
        )
    except:
        return None

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# Generate a JWT access token for the authenticated user
def create_access_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

# Create a session factory for database interactions
Session = sessionmaker(bind=engine)

# Token Extractor
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

# Dependency to get the current user based on the JWT token provided in the request
def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        session = Session()

        user = session.query(User).filter_by(
            id=user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

