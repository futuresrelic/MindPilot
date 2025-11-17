"""
Mood tracking router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

from database import get_db
from models import User, MoodLog
from auth import get_current_user
# Using OpenAI version - change to ai.mood_engine for Anthropic Claude
from ai.mood_engine_openai import generate_mood_reflection, analyze_mood_patterns

router = APIRouter(prefix="/mood", tags=["mood"])


class MoodCheckIn(BaseModel):
    mood_value: int  # 1-10
    tags: Optional[List[str]] = []
    note: Optional[str] = None


class MoodResponse(BaseModel):
    id: int
    mood_value: int
    tags: List[str]
    note: Optional[str]
    ai_reflection: Optional[str]
    created_at: datetime


@router.post("/checkin", response_model=MoodResponse)
def create_mood_checkin(
    checkin: MoodCheckIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a mood check-in with AI reflection"""

    # Validate mood value
    if checkin.mood_value < 1 or checkin.mood_value > 10:
        raise HTTPException(status_code=400, detail="Mood value must be between 1 and 10")

    # Get recent moods for context
    recent_moods = db.query(MoodLog).filter(
        MoodLog.user_id == user.id
    ).order_by(MoodLog.created_at.desc()).limit(7).all()

    recent_moods_data = [
        {"mood_value": m.mood_value, "tags": m.tags, "created_at": m.created_at}
        for m in recent_moods
    ]

    # Generate AI reflection
    ai_reflection = generate_mood_reflection(
        current_mood=checkin.mood_value,
        tags=checkin.tags or [],
        note=checkin.note,
        recent_moods=recent_moods_data,
        user=user
    )

    # Create mood log
    mood_log = MoodLog(
        user_id=user.id,
        mood_value=checkin.mood_value,
        tags=checkin.tags or [],
        note=checkin.note,
        ai_reflection=ai_reflection
    )

    db.add(mood_log)

    # Update user streak
    today = datetime.utcnow().date()
    if user.last_active:
        last_active_date = user.last_active.date()
        if last_active_date == today - timedelta(days=1):
            user.daily_streak += 1
        elif last_active_date != today:
            user.daily_streak = 1
    else:
        user.daily_streak = 1

    user.last_active = datetime.utcnow()

    db.commit()
    db.refresh(mood_log)

    return {
        "id": mood_log.id,
        "mood_value": mood_log.mood_value,
        "tags": mood_log.tags or [],
        "note": mood_log.note,
        "ai_reflection": mood_log.ai_reflection,
        "created_at": mood_log.created_at
    }


@router.get("/history")
def get_mood_history(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mood history"""

    cutoff = datetime.utcnow() - timedelta(days=days)

    moods = db.query(MoodLog).filter(
        MoodLog.user_id == user.id,
        MoodLog.created_at >= cutoff
    ).order_by(MoodLog.created_at.desc()).all()

    return {
        "moods": [
            {
                "id": m.id,
                "mood_value": m.mood_value,
                "tags": m.tags or [],
                "note": m.note,
                "ai_reflection": m.ai_reflection,
                "created_at": m.created_at
            }
            for m in moods
        ],
        "total": len(moods)
    }


@router.get("/patterns")
def get_mood_patterns(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mood pattern analysis"""

    patterns = analyze_mood_patterns(db, user.id, days)

    return {
        "patterns": patterns,
        "period_days": days
    }


@router.get("/today")
def get_today_mood(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has logged mood today"""

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    mood = db.query(MoodLog).filter(
        MoodLog.user_id == user.id,
        MoodLog.created_at >= today_start
    ).order_by(MoodLog.created_at.desc()).first()

    if not mood:
        return {"logged_today": False, "mood": None}

    return {
        "logged_today": True,
        "mood": {
            "id": mood.id,
            "mood_value": mood.mood_value,
            "tags": mood.tags or [],
            "note": mood.note,
            "ai_reflection": mood.ai_reflection,
            "created_at": mood.created_at
        }
    }
