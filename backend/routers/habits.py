"""
Habit tracking router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

from database import get_db
from models import User, Habit, HabitCompletion
from auth import get_current_user, check_premium

router = APIRouter(prefix="/habits", tags=["habits"])


class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = None
    recurrence: str = "daily"
    reminders: Optional[List[dict]] = []


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    recurrence: Optional[str] = None
    reminders: Optional[List[dict]] = None
    is_active: Optional[bool] = None


class HabitResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    recurrence: str
    reminders: List[dict]
    streak: int
    best_streak: int
    total_completions: int
    last_completed: Optional[datetime]
    is_active: bool
    created_at: datetime


@router.post("/", response_model=HabitResponse)
def create_habit(
    habit: HabitCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new habit"""

    # Check limit for free users
    if not check_premium(user):
        active_habits = db.query(Habit).filter(
            Habit.user_id == user.id,
            Habit.is_active == True
        ).count()

        if active_habits >= 2:
            raise HTTPException(
                status_code=403,
                detail="Free users can track up to 2 active habits. Upgrade to Premium for unlimited habits."
            )

    # Validate title
    if len(habit.title.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Habit title must be at least 3 characters"
        )

    # Create habit
    new_habit = Habit(
        user_id=user.id,
        title=habit.title,
        description=habit.description,
        recurrence=habit.recurrence,
        reminders=habit.reminders or [],
        streak=0,
        best_streak=0,
        total_completions=0,
        is_active=True
    )

    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)

    return {
        "id": new_habit.id,
        "title": new_habit.title,
        "description": new_habit.description,
        "recurrence": new_habit.recurrence,
        "reminders": new_habit.reminders or [],
        "streak": new_habit.streak,
        "best_streak": new_habit.best_streak,
        "total_completions": new_habit.total_completions,
        "last_completed": new_habit.last_completed,
        "is_active": new_habit.is_active,
        "created_at": new_habit.created_at
    }


@router.get("/", response_model=List[HabitResponse])
def get_habits(
    include_inactive: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user habits"""

    query = db.query(Habit).filter(Habit.user_id == user.id)

    if not include_inactive:
        query = query.filter(Habit.is_active == True)

    habits = query.order_by(Habit.created_at.desc()).all()

    return [
        {
            "id": h.id,
            "title": h.title,
            "description": h.description,
            "recurrence": h.recurrence,
            "reminders": h.reminders or [],
            "streak": h.streak,
            "best_streak": h.best_streak,
            "total_completions": h.total_completions,
            "last_completed": h.last_completed,
            "is_active": h.is_active,
            "created_at": h.created_at
        }
        for h in habits
    ]


@router.get("/{habit_id}")
def get_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit"""

    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Get recent completions
    recent_completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.completed_at.desc()).limit(30).all()

    return {
        "id": habit.id,
        "title": habit.title,
        "description": habit.description,
        "recurrence": habit.recurrence,
        "reminders": habit.reminders or [],
        "streak": habit.streak,
        "best_streak": habit.best_streak,
        "total_completions": habit.total_completions,
        "last_completed": habit.last_completed,
        "is_active": habit.is_active,
        "created_at": habit.created_at,
        "recent_completions": [
            {"id": c.id, "completed_at": c.completed_at}
            for c in recent_completions
        ]
    }


@router.patch("/{habit_id}")
def update_habit(
    habit_id: int,
    updates: HabitUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a habit"""

    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if updates.title is not None:
        habit.title = updates.title

    if updates.description is not None:
        habit.description = updates.description

    if updates.recurrence is not None:
        habit.recurrence = updates.recurrence

    if updates.reminders is not None:
        habit.reminders = updates.reminders

    if updates.is_active is not None:
        habit.is_active = updates.is_active

    db.commit()
    db.refresh(habit)

    return {
        "id": habit.id,
        "title": habit.title,
        "description": habit.description,
        "recurrence": habit.recurrence,
        "reminders": habit.reminders or [],
        "streak": habit.streak,
        "is_active": habit.is_active
    }


@router.post("/{habit_id}/complete")
def complete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a habit as completed for today"""

    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Check if already completed today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    existing_completion = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.completed_at >= today_start
    ).first()

    if existing_completion:
        raise HTTPException(
            status_code=400,
            detail="Habit already completed today"
        )

    # Create completion
    completion = HabitCompletion(
        habit_id=habit_id,
        completed_at=datetime.utcnow()
    )

    db.add(completion)

    # Update habit stats
    habit.total_completions += 1

    # Update streak
    if habit.last_completed:
        last_completed_date = habit.last_completed.date()
        today = datetime.utcnow().date()

        if last_completed_date == today - timedelta(days=1):
            # Consecutive day
            habit.streak += 1
        elif last_completed_date < today - timedelta(days=1):
            # Streak broken
            habit.streak = 1
        # If last_completed is today, do nothing (shouldn't happen due to check above)
    else:
        habit.streak = 1

    # Update best streak
    if habit.streak > habit.best_streak:
        habit.best_streak = habit.streak

    habit.last_completed = datetime.utcnow()

    db.commit()
    db.refresh(habit)

    return {
        "id": habit.id,
        "title": habit.title,
        "streak": habit.streak,
        "best_streak": habit.best_streak,
        "total_completions": habit.total_completions,
        "last_completed": habit.last_completed,
        "completion_id": completion.id
    }


@router.delete("/{habit_id}/complete")
def uncomplete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove today's completion (undo)"""

    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Find today's completion
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    completion = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id,
        HabitCompletion.completed_at >= today_start
    ).first()

    if not completion:
        raise HTTPException(status_code=404, detail="No completion found for today")

    # Delete completion
    db.delete(completion)

    # Update stats
    habit.total_completions -= 1
    habit.streak = max(0, habit.streak - 1)

    db.commit()

    return {"message": "Completion removed", "streak": habit.streak}


@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a habit"""

    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    db.delete(habit)
    db.commit()

    return {"message": "Habit deleted"}
