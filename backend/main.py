"""
MindPilot FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database import init_db
from routers import auth, mood, journal, habits, sleep, insights, audio, subscription

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    logger.info("Starting MindPilot API...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down MindPilot API...")


app = FastAPI(
    title="MindPilot API",
    description="AI-powered mental health and habit tracking companion",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(mood.router)
app.include_router(journal.router)
app.include_router(habits.router)
app.include_router(sleep.router)
app.include_router(insights.router)
app.include_router(audio.router)
app.include_router(subscription.router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "name": "MindPilot API",
        "version": "1.0.0",
        "status": "healthy",
        "message": "Welcome to MindPilot - Your AI Mental Health Companion"
    }


@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
