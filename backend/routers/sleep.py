"""
Sleep tracking router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import User, Sleep
from auth import get_current_user, check_premium

router = APIRouter(prefix="/sleep", tags=["sleep"])


class SleepLog(BaseModel):
    hours: float
    quality: Optional[int] = None  # 1-10
    notes: Optional[str] = None
    bedtime: Optional[datetime] = None
    waketime: Optional[datetime] = None


@router.post("/log")
def log_sleep(
    sleep_log: SleepLog,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log sleep data (Premium feature)"""

    if not check_premium(user):
        raise HTTPException(
            status_code=403,
            detail="Sleep tracking is a Premium feature"
        )

    # Validate
    if sleep_log.hours < 0 or sleep_log.hours > 24:
        raise HTTPException(status_code=400, detail="Invalid hours value")

    if sleep_log.quality and (sleep_log.quality < 1 or sleep_log.quality > 10):
        raise HTTPException(status_code=400, detail="Quality must be between 1 and 10")

    # Create sleep log
    sleep = Sleep(
        user_id=user.id,
        hours=sleep_log.hours,
        quality=sleep_log.quality,
        notes=sleep_log.notes,
        bedtime=sleep_log.bedtime,
        waketime=sleep_log.waketime
    )

    db.add(sleep)
    db.commit()
    db.refresh(sleep)

    return {
        "id": sleep.id,
        "hours": sleep.hours,
        "quality": sleep.quality,
        "notes": sleep.notes,
        "bedtime": sleep.bedtime,
        "waketime": sleep.waketime,
        "created_at": sleep.created_at
    }


@router.get("/history")
def get_sleep_history(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sleep history"""

    if not check_premium(user):
        raise HTTPException(
            status_code=403,
            detail="Sleep tracking is a Premium feature"
        )

    cutoff = datetime.utcnow() - timedelta(days=days)

    sleep_logs = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.created_at >= cutoff
    ).order_by(Sleep.created_at.desc()).all()

    return {
        "sleep_logs": [
            {
                "id": s.id,
                "hours": s.hours,
                "quality": s.quality,
                "notes": s.notes,
                "bedtime": s.bedtime,
                "waketime": s.waketime,
                "created_at": s.created_at
            }
            for s in sleep_logs
        ],
        "total": len(sleep_logs)
    }


@router.get("/stats")
def get_sleep_stats(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sleep statistics"""

    if not check_premium(user):
        raise HTTPException(
            status_code=403,
            detail="Sleep tracking is a Premium feature"
        )

    cutoff = datetime.utcnow() - timedelta(days=days)

    sleep_logs = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.created_at >= cutoff
    ).all()

    if not sleep_logs:
        return {
            "average_hours": 0,
            "average_quality": 0,
            "total_logs": 0
        }

    avg_hours = sum(s.hours for s in sleep_logs) / len(sleep_logs)
    qualities = [s.quality for s in sleep_logs if s.quality]
    avg_quality = sum(qualities) / len(qualities) if qualities else None

    return {
        "average_hours": round(avg_hours, 1),
        "average_quality": round(avg_quality, 1) if avg_quality else None,
        "total_logs": len(sleep_logs),
        "period_days": days
    }
