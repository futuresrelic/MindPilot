"""
AI Journal Analysis Engine
Summarizes journal entries, identifies themes, and provides supportive feedback
"""
import os
from typing import Dict, List
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def analyze_journal_entry(entry_text: str) -> Dict:
    """
    Analyze a journal entry and generate:
    - Summary
    - Key themes
    - Sentiment
    - Supportive feedback

    Args:
        entry_text: The journal entry text

    Returns:
        Dict with analysis results
    """

    prompt = f"""You are MindPilot, an empathetic AI wellness companion. Analyze this journal entry.

Journal Entry:
{entry_text}

Please provide:
1. A brief summary (1-2 sentences)
2. Key emotional themes (2-4 keywords like "gratitude", "stress", "excitement", "anxiety", "hope", etc.)
3. Overall sentiment (positive, neutral, negative, or mixed)
4. A sentiment score from 0 (very negative) to 1 (very positive)
5. Supportive feedback that validates their feelings and offers gentle encouragement

Format your response as JSON:
{{
  "summary": "...",
  "themes": ["theme1", "theme2", ...],
  "sentiment": "positive|neutral|negative|mixed",
  "sentiment_score": 0.0-1.0,
  "feedback": "..."
}}

Guidelines:
- Be warm and validating
- Never judge or criticize
- Acknowledge their emotions
- Keep feedback brief (2-3 sentences)
- No medical advice"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse the response
        import json
        result_text = response.content[0].text.strip()

        # Extract JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        result = json.loads(result_text)
        return result

    except Exception as e:
        # Fallback analysis
        return {
            "summary": "Thanks for sharing your thoughts today.",
            "themes": ["reflection"],
            "sentiment": "neutral",
            "sentiment_score": 0.5,
            "feedback": "Your feelings are valid. Taking time to write and reflect is a meaningful practice. Keep going. 💙"
        }


def generate_weekly_journal_summary(entries: List[Dict]) -> str:
    """
    Generate a summary of a week's worth of journal entries

    Args:
        entries: List of journal entries with their analyses

    Returns:
        str: Weekly summary
    """

    if not entries:
        return "You haven't journaled this week. Consider taking a few moments to reflect on your experiences."

    # Prepare entries for analysis
    entries_text = "\n\n".join([
        f"Day {i+1}: {entry['text'][:200]}..." if len(entry['text']) > 200 else f"Day {i+1}: {entry['text']}"
        for i, entry in enumerate(entries[:7])
    ])

    prompt = f"""You are MindPilot, an empathetic AI wellness companion. Summarize this week's journal entries.

Entries:
{entries_text}

Provide:
1. Overall themes from the week
2. Notable patterns or changes
3. A supportive message celebrating their consistency
4. One gentle suggestion for continued growth

Keep it warm, brief (3-4 sentences), and encouraging.
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
        return f"You journaled {len(entries)} times this week. Consistency is powerful. Keep reflecting on your experiences — it helps build self-awareness and emotional clarity. 🌟"


def extract_journal_insights(entries: List[Dict], days: int = 30) -> Dict:
    """
    Extract insights from journal entries over a period

    Returns:
        Dict with insights data
    """
    if not entries:
        return {
            "total_entries": 0,
            "common_themes": [],
            "avg_sentiment": 0.5,
            "writing_streak": 0
        }

    # Count themes
    theme_counts = {}
    sentiments = []

    for entry in entries:
        if "themes" in entry and entry["themes"]:
            for theme in entry["themes"]:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

        if "sentiment_score" in entry:
            sentiments.append(entry["sentiment_score"])

    common_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5

    return {
        "total_entries": len(entries),
        "common_themes": [theme for theme, _ in common_themes],
        "avg_sentiment": round(avg_sentiment, 2),
        "most_frequent_theme": common_themes[0][0] if common_themes else None
    }
