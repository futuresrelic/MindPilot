"""
Weekly Insights Generator
Analyzes user data and generates personalized weekly wellness reports
"""
import os
from typing import Dict, List
from datetime import datetime, timedelta
from anthropic import Anthropic
from sqlalchemy.orm import Session
from models import User, MoodLog, Journal, Habit, Sleep, HabitCompletion

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_weekly_insight(db: Session, user: User) -> Dict:
    """
    Generate comprehensive weekly wellness insight

    Args:
        db: Database session
        user: User object

    Returns:
        Dict with weekly insight data
    """

    # Get data from the past 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)

    # Mood data
    moods = db.query(MoodLog).filter(
        MoodLog.user_id == user.id,
        MoodLog.created_at >= week_ago
    ).all()

    # Journal data
    journals = db.query(Journal).filter(
        Journal.user_id == user.id,
        Journal.created_at >= week_ago
    ).all()

    # Habit data
    habits = db.query(Habit).filter(
        Habit.user_id == user.id,
        Habit.is_active == True
    ).all()

    # Get habit completions for the week
    habit_completions = {}
    for habit in habits:
        completions = db.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit.id,
            HabitCompletion.completed_at >= week_ago
        ).count()
        habit_completions[habit.title] = completions

    # Sleep data
    sleep_logs = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.created_at >= week_ago
    ).all()

    # Calculate statistics
    stats = calculate_weekly_stats(moods, journals, habits, habit_completions, sleep_logs)

    # Generate AI insight
    ai_summary = generate_ai_weekly_summary(stats, user)

    return {
        "stats": stats,
        "summary": ai_summary,
        "generated_at": datetime.utcnow().isoformat()
    }


def calculate_weekly_stats(
    moods: List[MoodLog],
    journals: List[Journal],
    habits: List[Habit],
    habit_completions: Dict[str, int],
    sleep_logs: List[Sleep]
) -> Dict:
    """Calculate statistics for the week"""

    stats = {}

    # Mood statistics
    if moods:
        mood_values = [m.mood_value for m in moods]
        stats["mood"] = {
            "average": round(sum(mood_values) / len(mood_values), 1),
            "highest": max(mood_values),
            "lowest": min(mood_values),
            "total_logs": len(moods),
            "trend": calculate_trend(mood_values)
        }

        # Collect all tags
        all_tags = []
        for mood in moods:
            if mood.tags:
                all_tags.extend(mood.tags)

        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        stats["mood"]["top_feelings"] = [tag for tag, _ in top_tags]
    else:
        stats["mood"] = None

    # Journal statistics
    if journals:
        sentiments = [j.sentiment_score for j in journals if j.sentiment_score]
        themes = []
        for j in journals:
            if j.themes:
                themes.extend(j.themes)

        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        stats["journal"] = {
            "total_entries": len(journals),
            "avg_sentiment": round(sum(sentiments) / len(sentiments), 2) if sentiments else 0.5,
            "top_themes": [theme for theme, _ in top_themes]
        }
    else:
        stats["journal"] = None

    # Habit statistics
    if habits:
        total_expected = len(habits) * 7  # 7 days
        total_completed = sum(habit_completions.values())
        completion_rate = (total_completed / total_expected * 100) if total_expected > 0 else 0

        best_habit = max(habit_completions.items(), key=lambda x: x[1]) if habit_completions else None

        stats["habits"] = {
            "total_habits": len(habits),
            "total_completions": total_completed,
            "completion_rate": round(completion_rate, 1),
            "best_habit": best_habit[0] if best_habit else None,
            "best_habit_count": best_habit[1] if best_habit else 0
        }
    else:
        stats["habits"] = None

    # Sleep statistics
    if sleep_logs:
        avg_hours = sum(s.hours for s in sleep_logs) / len(sleep_logs)
        qualities = [s.quality for s in sleep_logs if s.quality]
        avg_quality = sum(qualities) / len(qualities) if qualities else None

        stats["sleep"] = {
            "total_logs": len(sleep_logs),
            "avg_hours": round(avg_hours, 1),
            "avg_quality": round(avg_quality, 1) if avg_quality else None
        }
    else:
        stats["sleep"] = None

    return stats


def calculate_trend(values: List[float]) -> str:
    """Calculate trend from a list of values"""
    if len(values) < 3:
        return "neutral"

    recent = sum(values[-3:]) / 3
    older = sum(values[:3]) / 3

    if recent > older + 1:
        return "improving"
    elif recent < older - 1:
        return "declining"
    else:
        return "stable"


def generate_ai_weekly_summary(stats: Dict, user: User) -> str:
    """
    Generate AI-powered weekly summary

    Args:
        stats: Weekly statistics
        user: User object

    Returns:
        str: Personalized weekly summary
    """

    # Build context from stats
    context_parts = []

    if stats.get("mood"):
        mood_data = stats["mood"]
        context_parts.append(
            f"Mood: Average {mood_data['average']}/10, {mood_data['total_logs']} check-ins, "
            f"trend is {mood_data['trend']}. "
            f"Top feelings: {', '.join(mood_data.get('top_feelings', []))}"
        )

    if stats.get("journal"):
        journal_data = stats["journal"]
        context_parts.append(
            f"Journaling: {journal_data['total_entries']} entries. "
            f"Themes: {', '.join(journal_data.get('top_themes', []))}"
        )

    if stats.get("habits"):
        habit_data = stats["habits"]
        context_parts.append(
            f"Habits: {habit_data['completion_rate']}% completion rate. "
            f"Best habit: {habit_data.get('best_habit', 'N/A')} ({habit_data.get('best_habit_count', 0)} times)"
        )

    if stats.get("sleep"):
        sleep_data = stats["sleep"]
        quality_text = f", quality {sleep_data['avg_quality']}/10" if sleep_data['avg_quality'] else ""
        context_parts.append(
            f"Sleep: Average {sleep_data['avg_hours']} hours{quality_text}"
        )

    context = "\n".join(context_parts)

    prompt = f"""You are MindPilot, an empathetic AI wellness companion. Generate a warm, personalized weekly summary.

User's week:
{context}

Create a supportive summary (4-5 sentences) that:
1. Highlights their achievements and progress
2. Acknowledges any challenges
3. Identifies one pattern or insight
4. Offers one encouraging suggestion for next week
5. Celebrates their commitment to wellness

Tone: Warm, supportive, motivational, like a caring friend.
"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response.content[0].text.strip()
        return summary

    except Exception:
        # Fallback summary
        return generate_fallback_summary(stats)


def generate_fallback_summary(stats: Dict) -> str:
    """Generate fallback summary when AI is unavailable"""

    parts = ["Here's your week at a glance:"]

    if stats.get("mood"):
        mood = stats["mood"]
        parts.append(f"You tracked your mood {mood['total_logs']} times with an average of {mood['average']}/10.")

    if stats.get("habits"):
        habit = stats["habits"]
        parts.append(f"You completed {habit['total_completions']} habit check-ins with a {habit['completion_rate']}% success rate.")

    if stats.get("journal"):
        journal = stats["journal"]
        parts.append(f"You journaled {journal['total_entries']} times this week.")

    parts.append("Keep up the great work on your wellness journey! Every small step counts. 🌟")

    return " ".join(parts)


def generate_habit_suggestion(db: Session, user: User, stats: Dict) -> str:
    """
    Generate AI suggestion for a new habit based on user patterns

    Args:
        db: Database session
        user: User object
        stats: Recent statistics

    Returns:
        str: Habit suggestion
    """

    prompt = f"""You are MindPilot, an AI wellness companion. Based on this user's patterns, suggest ONE new habit.

User's goals: {', '.join(user.goals) if user.goals else 'general wellness'}

Recent patterns:
- {stats}

Suggest a small, achievable habit (one sentence) that:
- Aligns with their goals
- Addresses a gap in their wellness routine
- Is specific and actionable
- Takes 5-15 minutes

Example: "Try a 5-minute evening gratitude practice before bed to improve sleep quality."
"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        suggestion = response.content[0].text.strip()
        return suggestion

    except Exception:
        return "Try adding a 5-minute breathing practice each morning to start your day with calm and focus."
