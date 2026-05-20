from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append('../database') # Add the database directory to the path to import database modules
from database import engine
from models import User

from schemas.signup_schema import SignupRequest
from auth_utils import hash_password
from datetime import datetime, timezone

from schemas.login_schema import LoginRequest

from auth_utils import (
    verify_password,
    create_access_token
)

router = APIRouter()

Session = sessionmaker(bind=engine)

@router.post("/signup")
def signup(request: SignupRequest):
    session = Session()
    
    try:
        # Check if user with the same email already exists
        existing_user = session.query(User).filter_by(email=request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password before storing it
        hashed_password = hash_password(request.password)
        
        # Create a new user instance
        new_user = User(email=request.email, 
                        password_hash=hashed_password,
                        created_at=datetime.now(timezone.utc))
        
        # Add and commit the new user to the database
        session.add(new_user)
        session.commit()
        
        return {"message": "User registered successfully"}
    
    finally:
        session.close()

@router.post("/login")
def login(request: LoginRequest):
    session = Session()

    try:
        # Find user
        user = session.query(User).filter_by(
            email=request.email
        ).first()

        # User not found
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email"
            )

        # Password check
        valid_password = verify_password(
            request.password,
            user.password_hash
        )

        if not valid_password:
            raise HTTPException(
                status_code=401,
                detail="Invalid password"
            )

        # Generate JWT
        token = create_access_token(user.id)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:
        session.close()