"""
Insights and analytics router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import User, Insight
from auth import get_current_user, check_premium
from ai.weekly_insights import generate_weekly_insight, generate_habit_suggestion

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/weekly")
def get_weekly_insights(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate weekly wellness insights (Premium feature)"""

    if not check_premium(user):
        raise HTTPException(
            status_code=403,
            detail="Weekly insights are a Premium feature"
        )

    # Generate fresh insight
    insight_data = generate_weekly_insight(db, user)

    # Save insight to database
    insight = Insight(
        user_id=user.id,
        text=insight_data["summary"],
        insight_type="weekly",
        data=insight_data["stats"]
    )

    db.add(insight)
    db.commit()

    return {
        "summary": insight_data["summary"],
        "stats": insight_data["stats"],
        "generated_at": insight_data["generated_at"]
    }


@router.get("/history")
def get_insights_history(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get past insights"""

    insights = db.query(Insight).filter(
        Insight.user_id == user.id
    ).order_by(Insight.date.desc()).limit(limit).all()

    return {
        "insights": [
            {
                "id": i.id,
                "text": i.text,
                "type": i.insight_type,
                "data": i.data,
                "date": i.date
            }
            for i in insights
        ],
        "total": len(insights)
    }


@router.get("/habit-suggestion")
def get_habit_suggestion(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered habit suggestion based on user patterns"""

    # Get recent data for context
    week_ago = datetime.utcnow() - timedelta(days=7)

    from models import MoodLog, Journal, Habit

    recent_moods = db.query(MoodLog).filter(
        MoodLog.user_id == user.id,
        MoodLog.created_at >= week_ago
    ).all()

    recent_journals = db.query(Journal).filter(
        Journal.user_id == user.id,
        Journal.created_at >= week_ago
    ).all()

    active_habits = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True
    ).count()

    stats = {
        "mood_average": sum(m.mood_value for m in recent_moods) / len(recent_moods) if recent_moods else 5,
        "journal_count": len(recent_journals),
        "active_habits": active_habits,
        "user_goals": user.goals or []
    }

    suggestion = generate_habit_suggestion(db, user, stats)

    return {
        "suggestion": suggestion,
        "context": stats
    }


@router.get("/dashboard")
def get_dashboard_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall dashboard statistics"""

    from models import MoodLog, Journal, Habit, HabitCompletion, Sleep

    # Get today's data
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    today_mood = db.query(MoodLog).filter(
        MoodLog.user_id == user.id,
        MoodLog.created_at >= today_start
    ).first()

    # Get habit completions today
    active_habits = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True
    ).all()

    today_completions = 0
    for habit in active_habits:
        completion = db.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit.id,
            HabitCompletion.completed_at >= today_start
        ).first()
        if completion:
            today_completions += 1

    # Get week stats
    week_ago = datetime.utcnow() - timedelta(days=7)

    week_moods = db.query(MoodLog).filter(
        MoodLog.user_id == user.id,
        MoodLog.created_at >= week_ago
    ).all()

    week_journals = db.query(Journal).filter(
        Journal.user_id == user.id,
        Journal.created_at >= week_ago
    ).count()

    week_sleep = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.created_at >= week_ago
    ).all()

    return {
        "today": {
            "mood_logged": bool(today_mood),
            "mood_value": today_mood.mood_value if today_mood else None,
            "habits_completed": today_completions,
            "total_active_habits": len(active_habits)
        },
        "week": {
            "mood_logs": len(week_moods),
            "avg_mood": round(sum(m.mood_value for m in week_moods) / len(week_moods), 1) if week_moods else 0,
            "journal_entries": week_journals,
            "sleep_logs": len(week_sleep),
            "avg_sleep": round(sum(s.hours for s in week_sleep) / len(week_sleep), 1) if week_sleep else 0
        },
        "streak": user.daily_streak,
        "subscription": user.subscription_status
    }
