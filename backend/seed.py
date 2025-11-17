"""
Seed script to populate database with sample data
"""
import sys
from database import SessionLocal, init_db
from models import AudioContent

def seed_audio_content():
    """Seed sample audio content"""
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(AudioContent).first()
        if existing:
            print("Database already seeded. Skipping...")
            return

        # Sample audio content
        audio_samples = [
            # Meditation - Free
            {
                "title": "5-Minute Morning Meditation",
                "description": "Start your day with calm and intention",
                "category": "meditation",
                "duration_seconds": 300,
                "audio_url": "https://example.com/audio/morning-meditation.mp3",
                "thumbnail_url": "https://example.com/thumbnails/morning.jpg",
                "is_premium": False,
                "tags": ["morning", "beginner", "calm"]
            },
            {
                "title": "Body Scan Relaxation",
                "description": "Release tension with progressive body awareness",
                "category": "meditation",
                "duration_seconds": 600,
                "audio_url": "https://example.com/audio/body-scan.mp3",
                "thumbnail_url": "https://example.com/thumbnails/body-scan.jpg",
                "is_premium": False,
                "tags": ["relaxation", "body", "tension"]
            },

            # Breathing - Free
            {
                "title": "Box Breathing",
                "description": "4-4-4-4 breathing pattern for instant calm",
                "category": "breathing",
                "duration_seconds": 240,
                "audio_url": "https://example.com/audio/box-breathing.mp3",
                "thumbnail_url": "https://example.com/thumbnails/breathing.jpg",
                "is_premium": False,
                "tags": ["breathing", "anxiety", "quick"]
            },

            # Sleep - Premium
            {
                "title": "Deep Sleep Hypnosis",
                "description": "Drift into restorative sleep with guided relaxation",
                "category": "sleep",
                "duration_seconds": 1200,
                "audio_url": "https://example.com/audio/sleep-hypnosis.mp3",
                "thumbnail_url": "https://example.com/thumbnails/sleep.jpg",
                "is_premium": True,
                "tags": ["sleep", "insomnia", "long"]
            },
            {
                "title": "Bedtime Wind Down",
                "description": "Gentle transition from day to night",
                "category": "sleep",
                "duration_seconds": 900,
                "audio_url": "https://example.com/audio/bedtime.mp3",
                "thumbnail_url": "https://example.com/thumbnails/bedtime.jpg",
                "is_premium": True,
                "tags": ["sleep", "evening", "calm"]
            },

            # Focus - Premium
            {
                "title": "Focus Flow State",
                "description": "Binaural beats for deep concentration",
                "category": "focus",
                "duration_seconds": 1800,
                "audio_url": "https://example.com/audio/focus.mp3",
                "thumbnail_url": "https://example.com/thumbnails/focus.jpg",
                "is_premium": True,
                "tags": ["focus", "work", "productivity"]
            },

            # Stress Relief - Mix
            {
                "title": "Stress Release Meditation",
                "description": "Let go of worry and tension",
                "category": "stress",
                "duration_seconds": 480,
                "audio_url": "https://example.com/audio/stress-release.mp3",
                "thumbnail_url": "https://example.com/thumbnails/stress.jpg",
                "is_premium": False,
                "tags": ["stress", "anxiety", "release"]
            },
            {
                "title": "Nature Sounds for Calm",
                "description": "Ocean waves and gentle rain",
                "category": "stress",
                "duration_seconds": 1200,
                "audio_url": "https://example.com/audio/nature.mp3",
                "thumbnail_url": "https://example.com/thumbnails/nature.jpg",
                "is_premium": True,
                "tags": ["nature", "calm", "background"]
            },

            # Meditation - Premium
            {
                "title": "Loving-Kindness Meditation",
                "description": "Cultivate compassion for yourself and others",
                "category": "meditation",
                "duration_seconds": 720,
                "audio_url": "https://example.com/audio/loving-kindness.mp3",
                "thumbnail_url": "https://example.com/thumbnails/loving-kindness.jpg",
                "is_premium": True,
                "tags": ["meditation", "compassion", "heart"]
            },
            {
                "title": "Evening Gratitude",
                "description": "Reflect on the gifts of your day",
                "category": "meditation",
                "duration_seconds": 420,
                "audio_url": "https://example.com/audio/gratitude.mp3",
                "thumbnail_url": "https://example.com/thumbnails/gratitude.jpg",
                "is_premium": True,
                "tags": ["gratitude", "evening", "reflection"]
            }
        ]

        # Add to database
        for audio_data in audio_samples:
            audio = AudioContent(**audio_data)
            db.add(audio)

        db.commit()
        print(f"✅ Successfully seeded {len(audio_samples)} audio content items")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding database...")
    seed_audio_content()
    print("Done!")
