"""
AI Mood Reflection Engine (OpenAI Version)
Generates empathetic, supportive responses to mood check-ins
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import MoodLog, User

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_mood_reflection(
    current_mood: int,
    tags: List[str],
    note: Optional[str],
    recent_moods: List[Dict],
    user: User
) -> str:
    """
    Generate an AI reflection on the user's mood

    Args:
        current_mood: 1-10 mood value
        tags: List of mood tags like ["stress", "tired", "focused"]
        note: Optional user note
        recent_moods: List of recent mood logs for context
        user: User object

    Returns:
        str: Empathetic, supportive reflection message
    """

    # Build context from recent moods
    mood_context = ""
    if recent_moods:
        mood_values = [m["mood_value"] for m in recent_moods[-7:]]
        avg_mood = sum(mood_values) / len(mood_values)

        if current_mood < avg_mood - 1.5:
            trend = "lower than your recent average"
        elif current_mood > avg_mood + 1.5:
            trend = "higher than your recent average"
        else:
            trend = "around your usual level"

        mood_context = f"Your mood today ({current_mood}/10) is {trend}. "
    else:
        mood_context = f"You're feeling {current_mood}/10 today. "

    # Build tags context
    tags_text = ", ".join(tags) if tags else "no specific tags"

    # Build note context
    note_text = f"You mentioned: '{note}'" if note else ""

    prompt = f"""You are MindPilot, an empathetic AI wellness companion. Generate a brief, supportive reflection on this mood check-in.

Context:
- {mood_context}
- Tags: {tags_text}
- {note_text}

Guidelines:
- Be warm, empathetic, and supportive
- Keep it brief (2-3 sentences max)
- Provide one small, actionable suggestion if mood is low
- Celebrate if mood is high
- Never give medical advice
- Use calm, gentle language
- Be age-appropriate for all users

Generate a supportive reflection:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fast and cheap! Can upgrade to gpt-4 later
            max_tokens=200,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are MindPilot, a warm and empathetic mental wellness companion."},
                {"role": "user", "content": prompt}
            ]
        )

        reflection = response.choices[0].message.content.strip()
        return reflection

    except Exception as e:
        # Fallback to template-based responses
        return generate_fallback_reflection(current_mood, tags)


def generate_fallback_reflection(mood: int, tags: List[str]) -> str:
    """Fallback reflection when AI is unavailable"""

    if mood <= 3:
        return "I notice you're having a tough time. Remember, difficult moments pass. Try taking three deep breaths or a short walk outside. You've got this. 💙"
    elif mood <= 5:
        return "Things feel challenging right now. That's okay. Small steps matter — maybe try one thing that usually brings you comfort today. 🌸"
    elif mood <= 7:
        return "You're doing alright today. Keep going with what's working for you. Remember to be kind to yourself. ✨"
    else:
        return "It's wonderful to see you feeling good! Enjoy this moment and the positive energy you have today. 🌟"


def analyze_mood_patterns(db: Session, user_id: int, days: int = 7) -> Dict:
    """
    Analyze mood patterns over time

    Returns:
        Dict with pattern analysis
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    moods = db.query(MoodLog).filter(
        MoodLog.user_id == user_id,
        MoodLog.created_at >= cutoff_date
    ).order_by(MoodLog.created_at).all()

    if not moods:
        return {"average": 0, "trend": "neutral", "consistency": 0}

    mood_values = [m.mood_value for m in moods]
    average = sum(mood_values) / len(mood_values)

    # Calculate trend
    if len(mood_values) >= 3:
        recent_avg = sum(mood_values[-3:]) / 3
        older_avg = sum(mood_values[:3]) / 3

        if recent_avg > older_avg + 1:
            trend = "improving"
        elif recent_avg < older_avg - 1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "neutral"

    # Calculate consistency (lower std dev = more consistent)
    if len(mood_values) > 1:
        mean = sum(mood_values) / len(mood_values)
        variance = sum((x - mean) ** 2 for x in mood_values) / len(mood_values)
        std_dev = variance ** 0.5
        consistency = max(0, 10 - std_dev)
    else:
        consistency = 10

    # Collect all tags
    all_tags = []
    for mood in moods:
        if mood.tags:
            all_tags.extend(mood.tags)

    # Count tag frequencies
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "average": round(average, 1),
        "trend": trend,
        "consistency": round(consistency, 1),
        "common_tags": [tag for tag, _ in common_tags],
        "total_logs": len(moods)
    }
