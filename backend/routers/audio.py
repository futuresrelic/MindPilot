"""
Audio content and listening sessions router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from database import get_db
from models import User, AudioContent, ListeningSession
from auth import get_current_user, check_premium

router = APIRouter(prefix="/audio", tags=["audio"])


class SessionCreate(BaseModel):
    audio_id: str
    duration_seconds: int
    completed: bool = False


@router.get("/content")
def get_audio_content(
    category: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available audio content"""

    query = db.query(AudioContent)

    # Free users only see non-premium content
    if not check_premium(user):
        query = query.filter(AudioContent.is_premium == False)

    if category:
        query = query.filter(AudioContent.category == category)

    content = query.order_by(AudioContent.created_at.desc()).all()

    return {
        "content": [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "duration_seconds": c.duration_seconds,
                "audio_url": c.audio_url,
                "thumbnail_url": c.thumbnail_url,
                "is_premium": c.is_premium,
                "tags": c.tags or []
            }
            for c in content
        ],
        "total": len(content)
    }


@router.get("/content/{content_id}")
def get_audio_detail(
    content_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific audio content details"""

    content = db.query(AudioContent).filter(AudioContent.id == content_id).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check if premium content and user has access
    if content.is_premium and not check_premium(user):
        raise HTTPException(
            status_code=403,
            detail="This is premium content. Upgrade to access."
        )

    return {
        "id": content.id,
        "title": content.title,
        "description": content.description,
        "category": content.category,
        "duration_seconds": content.duration_seconds,
        "audio_url": content.audio_url,
        "thumbnail_url": content.thumbnail_url,
        "is_premium": content.is_premium,
        "tags": content.tags or []
    }


@router.post("/sessions")
def create_listening_session(
    session: SessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a listening session"""

    # Create session
    listening_session = ListeningSession(
        user_id=user.id,
        audio_id=session.audio_id,
        duration_seconds=session.duration_seconds,
        completed=session.completed,
        completed_at=datetime.utcnow() if session.completed else None
    )

    db.add(listening_session)
    db.commit()
    db.refresh(listening_session)

    return {
        "id": listening_session.id,
        "audio_id": listening_session.audio_id,
        "duration_seconds": listening_session.duration_seconds,
        "completed": listening_session.completed,
        "created_at": listening_session.created_at
    }


@router.get("/sessions")
def get_listening_history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get listening history"""

    sessions = db.query(ListeningSession).filter(
        ListeningSession.user_id == user.id
    ).order_by(ListeningSession.created_at.desc()).limit(limit).all()

    return {
        "sessions": [
            {
                "id": s.id,
                "audio_id": s.audio_id,
                "audio_title": s.audio_title,
                "duration_seconds": s.duration_seconds,
                "completed": s.completed,
                "completed_at": s.completed_at,
                "created_at": s.created_at
            }
            for s in sessions
        ],
        "total": len(sessions)
    }


@router.get("/categories")
def get_categories(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available categories"""

    # Get distinct categories
    categories = db.query(AudioContent.category).distinct().all()

    return {
        "categories": [cat[0] for cat in categories if cat[0]]
    }
