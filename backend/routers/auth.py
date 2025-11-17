"""
Authentication router - signup, login, user management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from database import get_db
from models import User
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    age_range: Optional[str] = None
    goals: Optional[List[str]] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserUpdate(BaseModel):
    age_range: Optional[str] = None
    goals: Optional[List[str]] = None
    theme: Optional[str] = None


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account"""

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        age_range=request.age_range,
        goals=request.goals,
        subscription_status="free",
        daily_streak=0
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "age_range": new_user.age_range,
            "goals": new_user.goals,
            "subscription_status": new_user.subscription_status,
            "daily_streak": new_user.daily_streak
        }
    }


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""

    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Update last active
    user.last_active = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "age_range": user.age_range,
            "goals": user.goals,
            "subscription_status": user.subscription_status,
            "daily_streak": user.daily_streak,
            "theme": user.theme
        }
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """Get current user profile"""

    return {
        "id": user.id,
        "email": user.email,
        "age_range": user.age_range,
        "goals": user.goals,
        "subscription_status": user.subscription_status,
        "subscription_expires": user.subscription_expires,
        "daily_streak": user.daily_streak,
        "theme": user.theme,
        "created_at": user.created_at
    }


@router.patch("/me")
def update_me(
    updates: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""

    if updates.age_range is not None:
        user.age_range = updates.age_range

    if updates.goals is not None:
        user.goals = updates.goals

    if updates.theme is not None:
        user.theme = updates.theme

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "age_range": user.age_range,
        "goals": user.goals,
        "theme": user.theme
    }
