"""
Backend API Tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db
from models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Test fixtures
@pytest.fixture
def test_user():
    """Create a test user"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "age_range": "25-34",
            "goals": ["stress", "mindfulness"]
        }
    )
    assert response.status_code == 200
    return response.json()


def test_health_check():
    """Test API health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_signup():
    """Test user signup"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"


def test_login(test_user):
    """Test user login"""
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_mood_checkin(test_user):
    """Test mood check-in"""
    token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/mood/checkin",
        json={
            "mood_value": 7,
            "tags": ["happy", "energized"],
            "note": "Feeling great today!"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mood_value"] == 7
    assert "ai_reflection" in data


def test_journal_entry(test_user):
    """Test journal entry creation"""
    token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/journal/entries",
        json={
            "text": "Today was a productive day. I completed my morning meditation and felt very focused throughout the day."
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "ai_summary" in data
    assert "themes" in data


def test_create_habit(test_user):
    """Test habit creation"""
    token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/habits/",
        json={
            "title": "Morning Meditation",
            "description": "10 minutes of mindfulness",
            "recurrence": "daily"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Morning Meditation"
    assert data["streak"] == 0


def test_complete_habit(test_user):
    """Test habit completion"""
    token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create habit
    create_response = client.post(
        "/habits/",
        json={"title": "Daily Walk"},
        headers=headers
    )
    habit_id = create_response.json()["id"]

    # Complete habit
    complete_response = client.post(
        f"/habits/{habit_id}/complete",
        headers=headers
    )
    assert complete_response.status_code == 200
    data = complete_response.json()
    assert data["streak"] == 1


def test_dashboard(test_user):
    """Test dashboard endpoint"""
    token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/insights/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "today" in data
    assert "week" in data


def test_unauthorized_access():
    """Test that endpoints require authentication"""
    response = client.get("/auth/me")
    assert response.status_code == 403  # No token


def test_mood_history(test_user):
    """Test mood history retrieval"""
    token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/mood/history?days=30", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "moods" in data


def test_subscription_plans():
    """Test subscription plans endpoint"""
    response = client.get("/subscription/plans")
    assert response.status_code == 200
    data = response.json()
    assert "plans" in data
    assert len(data["plans"]) >= 2  # monthly and yearly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
