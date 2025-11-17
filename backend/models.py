"""
Database models for MindPilot
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age_range = Column(String(50))
    subscription_status = Column(String(50), default="free")  # free, premium, trial
    subscription_id = Column(String(255))
    subscription_expires = Column(DateTime)
    daily_streak = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow)
    goals = Column(JSON)  # ["stress", "mindfulness", "focus", "sleep"]
    theme = Column(String(50), default="light")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
    journals = relationship("Journal", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    sleep_logs = relationship("Sleep", back_populates="user", cascade="all, delete-orphan")
    listening_sessions = relationship("ListeningSession", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")


class MoodLog(Base):
    __tablename__ = "mood_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_value = Column(Integer, nullable=False)  # 1-10
    tags = Column(JSON)  # ["stress", "tired", "focused", etc.]
    note = Column(Text)
    ai_reflection = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="mood_logs")


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    ai_summary = Column(Text)
    ai_cbt_suggestion = Column(Text)
    sentiment = Column(String(50))  # positive, neutral, negative, mixed
    sentiment_score = Column(Float)  # 0-1
    themes = Column(JSON)  # ["stress", "anxiety", "gratitude", etc.]
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="journals")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    recurrence = Column(String(50), default="daily")  # daily, weekly, custom
    reminders = Column(JSON)  # [{"time": "09:00", "enabled": true}]
    streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)
    last_completed = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="habits")
    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")


class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    completed_at = Column(DateTime, server_default=func.now())

    habit = relationship("Habit", back_populates="completions")


class Sleep(Base):
    __tablename__ = "sleep_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hours = Column(Float, nullable=False)
    quality = Column(Integer)  # 1-10
    notes = Column(Text)
    bedtime = Column(DateTime)
    waketime = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="sleep_logs")


class ListeningSession(Base):
    __tablename__ = "listening_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audio_id = Column(String(255), nullable=False)
    audio_title = Column(String(255))
    duration_seconds = Column(Integer)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="listening_sessions")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    insight_type = Column(String(50))  # weekly, monthly, trend, suggestion
    data = Column(JSON)  # supporting data for the insight
    date = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="insights")


class AudioContent(Base):
    __tablename__ = "audio_content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # meditation, sleep, breathing, focus, stress
    duration_seconds = Column(Integer, nullable=False)
    audio_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    is_premium = Column(Boolean, default=False)
    tags = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
