"""
CBT (Cognitive Behavioral Therapy) Suggestion Engine
Provides supportive, evidence-based suggestions for common thought patterns
"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_cbt_suggestion(
    journal_text: str,
    themes: List[str],
    sentiment: str
) -> str:
    """
    Generate CBT-style supportive suggestions based on journal content

    Args:
        journal_text: The journal entry
        themes: Identified themes from the entry
        sentiment: Sentiment analysis result

    Returns:
        str: CBT-style suggestion
    """

    # Identify potential cognitive patterns
    patterns = identify_cognitive_patterns(journal_text, themes)

    prompt = f"""You are MindPilot, an empathetic AI wellness companion trained in CBT principles.

User's journal entry themes: {', '.join(themes)}
Potential cognitive patterns: {', '.join(patterns)}
Overall sentiment: {sentiment}

Provide a brief, supportive CBT-style suggestion (2-3 sentences) that:
- Validates their feelings
- Gently introduces a CBT reframing technique if applicable
- Offers a small, actionable practice
- Uses warm, non-clinical language
- Never diagnoses or provides medical advice

Focus on common CBT techniques like:
- Cognitive reframing
- Thought challenging
- Behavioral activation
- Mindfulness
- Gratitude practices
- Self-compassion

Be supportive and gentle, not prescriptive or clinical."""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        suggestion = response.content[0].text.strip()
        return suggestion

    except Exception:
        # Fallback to pattern-based suggestions
        return generate_fallback_cbt_suggestion(patterns, themes)


def identify_cognitive_patterns(text: str, themes: List[str]) -> List[str]:
    """
    Identify potential cognitive patterns from text and themes

    Returns:
        List of identified patterns
    """
    patterns = []

    text_lower = text.lower()

    # All-or-nothing thinking
    if any(word in text_lower for word in ["always", "never", "completely", "totally", "every time"]):
        patterns.append("black-and-white thinking")

    # Catastrophizing
    if any(word in text_lower for word in ["disaster", "terrible", "awful", "worst", "horrible", "ruin"]):
        patterns.append("catastrophizing")

    # Should statements
    if any(word in text_lower for word in ["should", "must", "have to", "need to", "supposed to"]):
        patterns.append("rigid expectations")

    # Mind reading
    if any(phrase in text_lower for phrase in ["they think", "they probably", "they must think", "everyone thinks"]):
        patterns.append("mind reading")

    # Overgeneralization
    if "everyone" in text_lower or "no one" in text_lower or "everything" in text_lower:
        patterns.append("overgeneralization")

    # Theme-based patterns
    if "anxiety" in themes or "worry" in themes:
        patterns.append("anxious thoughts")

    if "stress" in themes:
        patterns.append("stress response")

    if "rumination" in themes or "overthinking" in text_lower:
        patterns.append("rumination")

    if "self-criticism" in themes or any(word in text_lower for word in ["my fault", "i'm bad", "i'm terrible"]):
        patterns.append("self-criticism")

    return patterns if patterns else ["general reflection"]


def generate_fallback_cbt_suggestion(patterns: List[str], themes: List[str]) -> str:
    """
    Generate fallback CBT suggestions when AI is unavailable
    """

    if "catastrophizing" in patterns:
        return "When worries feel overwhelming, try asking: 'What's the most likely outcome?' Often our minds jump to worst-case scenarios. Grounding yourself in probability can help ease anxiety."

    if "black-and-white thinking" in patterns:
        return "Life rarely fits into 'always' or 'never' categories. When you notice absolute thinking, pause and look for the gray areas — the partial successes, the small progress, the nuance."

    if "self-criticism" in patterns:
        return "You're being hard on yourself. Try speaking to yourself like you would a good friend — with kindness and understanding. What would you say to them? Say that to yourself."

    if "rigid expectations" in patterns:
        return "Notice those 'should' statements? They can create unnecessary pressure. Try reframing: instead of 'I should,' try 'I'd like to' or 'It would be helpful if.' Give yourself some flexibility."

    if "anxiety" in themes or "anxious thoughts" in patterns:
        return "Anxiety often pulls us into the future. Try bringing yourself back to this moment: What can you see, hear, touch right now? Ground yourself in the present."

    if "stress" in themes:
        return "Stress is your body's signal. Listen to it with compassion. What one small thing could give you relief right now? Even five minutes of gentle breathing can help."

    if "rumination" in patterns:
        return "Notice you're looping on this thought? Try setting a 'worry timer' — give yourself 10 minutes to think it through, then consciously shift your attention to something else."

    # Default
    return "Acknowledge your feelings without judgment. They're valid. Then ask yourself: What one small, kind action could I take for myself right now? Start there."


def analyze_cbt_progress(journal_entries: List[Dict]) -> Dict:
    """
    Analyze progress in thought patterns over time

    Args:
        journal_entries: List of journal entries with themes and sentiment

    Returns:
        Dict with progress analysis
    """

    if len(journal_entries) < 5:
        return {
            "progress": "insufficient_data",
            "message": "Keep journaling to track your thought pattern progress over time."
        }

    # Split into early and recent entries
    half = len(journal_entries) // 2
    early_entries = journal_entries[:half]
    recent_entries = journal_entries[half:]

    # Calculate average sentiment
    early_sentiment = sum(e.get("sentiment_score", 0.5) for e in early_entries) / len(early_entries)
    recent_sentiment = sum(e.get("sentiment_score", 0.5) for e in recent_entries) / len(recent_entries)

    # Determine progress
    if recent_sentiment > early_sentiment + 0.1:
        progress = "improving"
        message = "Your emotional tone has been shifting positively. The awareness you're building through journaling is working. Keep it up! 🌟"
    elif recent_sentiment < early_sentiment - 0.1:
        progress = "challenging"
        message = "You've been going through a tough period. Remember, difficult phases are temporary. Be extra gentle with yourself right now. 💙"
    else:
        progress = "stable"
        message = "You're maintaining emotional stability. Consistency in reflection is a strength. Keep nurturing this practice. ✨"

    return {
        "progress": progress,
        "early_sentiment": round(early_sentiment, 2),
        "recent_sentiment": round(recent_sentiment, 2),
        "message": message
    }
