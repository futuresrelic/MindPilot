"""
AI Journaling router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import User, Journal
from auth import get_current_user, check_premium
# Using OpenAI versions - change to ai.journal_engine and ai.cbt_engine for Anthropic Claude
from ai.journal_engine_openai import analyze_journal_entry, generate_weekly_journal_summary, extract_journal_insights
from ai.cbt_engine_openai import generate_cbt_suggestion

router = APIRouter(prefix="/journal", tags=["journal"])


class JournalEntry(BaseModel):
    text: str


class JournalResponse(BaseModel):
    id: int
    text: str
    ai_summary: Optional[str]
    ai_cbt_suggestion: Optional[str]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    themes: Optional[list]
    created_at: datetime


@router.post("/entries", response_model=JournalResponse)
def create_journal_entry(
    entry: JournalEntry,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new journal entry with AI analysis"""

    # Check daily limit for free users
    if not check_premium(user):
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_entries = db.query(Journal).filter(
            Journal.user_id == user.id,
            Journal.created_at >= today_start
        ).count()

        if today_entries >= 1:
            raise HTTPException(
                status_code=403,
                detail="Free users can create 1 journal entry per day. Upgrade to Premium for unlimited entries."
            )

    # Validate entry
    if len(entry.text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Journal entry must be at least 10 characters"
        )

    # Analyze entry with AI
    analysis = analyze_journal_entry(entry.text)

    # Generate CBT suggestion if premium
    cbt_suggestion = None
    if check_premium(user) and analysis.get("themes"):
        cbt_suggestion = generate_cbt_suggestion(
            entry.text,
            analysis.get("themes", []),
            analysis.get("sentiment", "neutral")
        )

    # Create journal entry
    journal = Journal(
        user_id=user.id,
        text=entry.text,
        ai_summary=analysis.get("summary"),
        ai_cbt_suggestion=cbt_suggestion,
        sentiment=analysis.get("sentiment"),
        sentiment_score=analysis.get("sentiment_score"),
        themes=analysis.get("themes", [])
    )

    db.add(journal)
    db.commit()
    db.refresh(journal)

    return {
        "id": journal.id,
        "text": journal.text,
        "ai_summary": journal.ai_summary,
        "ai_cbt_suggestion": journal.ai_cbt_suggestion,
        "sentiment": journal.sentiment,
        "sentiment_score": journal.sentiment_score,
        "themes": journal.themes,
        "created_at": journal.created_at
    }


@router.get("/entries")
def get_journal_entries(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's journal entries"""

    entries = db.query(Journal).filter(
        Journal.user_id == user.id
    ).order_by(Journal.created_at.desc()).limit(limit).offset(offset).all()

    total = db.query(Journal).filter(Journal.user_id == user.id).count()

    return {
        "entries": [
            {
                "id": e.id,
                "text": e.text,
                "ai_summary": e.ai_summary,
                "ai_cbt_suggestion": e.ai_cbt_suggestion,
                "sentiment": e.sentiment,
                "sentiment_score": e.sentiment_score,
                "themes": e.themes,
                "created_at": e.created_at
            }
            for e in entries
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/entries/{entry_id}")
def get_journal_entry(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific journal entry"""

    entry = db.query(Journal).filter(
        Journal.id == entry_id,
        Journal.user_id == user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    return {
        "id": entry.id,
        "text": entry.text,
        "ai_summary": entry.ai_summary,
        "ai_cbt_suggestion": entry.ai_cbt_suggestion,
        "sentiment": entry.sentiment,
        "sentiment_score": entry.sentiment_score,
        "themes": entry.themes,
        "created_at": entry.created_at
    }


@router.get("/weekly-summary")
def get_weekly_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated weekly journal summary (Premium feature)"""

    if not check_premium(user):
        raise HTTPException(
            status_code=403,
            detail="Weekly summaries are a Premium feature"
        )

    week_ago = datetime.utcnow() - timedelta(days=7)

    entries = db.query(Journal).filter(
        Journal.user_id == user.id,
        Journal.created_at >= week_ago
    ).order_by(Journal.created_at).all()

    if not entries:
        return {
            "summary": "You haven't journaled this week. Start writing to get personalized insights!",
            "entry_count": 0
        }

    entries_data = [
        {
            "text": e.text,
            "themes": e.themes,
            "sentiment": e.sentiment,
            "sentiment_score": e.sentiment_score
        }
        for e in entries
    ]

    summary = generate_weekly_journal_summary(entries_data)

    return {
        "summary": summary,
        "entry_count": len(entries),
        "period": "last_7_days"
    }


@router.get("/insights")
def get_journal_insights(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get journal insights over time"""

    cutoff = datetime.utcnow() - timedelta(days=days)

    entries = db.query(Journal).filter(
        Journal.user_id == user.id,
        Journal.created_at >= cutoff
    ).all()

    entries_data = [
        {
            "themes": e.themes,
            "sentiment": e.sentiment,
            "sentiment_score": e.sentiment_score,
            "created_at": e.created_at
        }
        for e in entries
    ]

    insights = extract_journal_insights(entries_data, days)

    return {
        "insights": insights,
        "period_days": days
    }
