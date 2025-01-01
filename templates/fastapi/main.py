from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uvicorn
import asyncio
import logging
from sqlalchemy.orm import Session
from db.database import db
from db.repository import WaitlistRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Waitlist Service API",
    description="API for managing waitlist entries using FastAPI",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Initializing database...")
        await db.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Dependency to get database session
def get_db():
    return next(db.get_db())

# Models
class WaitlistEntryCreate(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    name: Optional[str] = Field(None, description="Name of the user")
    comment: Optional[str] = Field(None, description="Additional comments")
    referral_source: Optional[str] = Field(None, description="How the user found out about the service")

class WaitlistEntryResponse(WaitlistEntryCreate):
    created_at: datetime = Field(default_factory=datetime.now)

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Waitlist Service API"}

@app.post("/waitlist", response_model=WaitlistEntryResponse)
async def add_to_waitlist(entry: WaitlistEntryCreate, db: Session = Depends(get_db)):
    """
    Add a new entry to the waitlist
    
    Parameters:
    - email: Required email address
    - name: Optional user name
    - comment: Optional additional comments
    - referral_source: Optional referral source
    
    Returns:
    - The created waitlist entry with timestamp
    """
    try:
        repo = WaitlistRepository(db)
        db_entry = repo.create_entry(
            email=entry.email,
            name=entry.name,
            comment=entry.comment,
            referral_source=entry.referral_source
        )
        
        logger.info(f"Created waitlist entry for email: {entry.email}")
        return WaitlistEntryResponse(
            email=db_entry.email,
            name=db_entry.name,
            comment=db_entry.comment,
            referral_source=db_entry.referral_source,
            created_at=db_entry.created_at
        )
    except ValueError as e:
        logger.warning(f"Duplicate entry attempt: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding waitlist entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/waitlist", response_model=List[WaitlistEntryResponse])
async def get_all_entries(db: Session = Depends(get_db)):
    """
    Get all waitlist entries
    """
    try:
        repo = WaitlistRepository(db)
        entries = repo.get_all_entries()
        return [
            WaitlistEntryResponse(
                email=entry.email,
                name=entry.name,
                comment=entry.comment,
                referral_source=entry.referral_source,
                created_at=entry.created_at
            ) for entry in entries
        ]
    except Exception as e:
        logger.error(f"Error fetching waitlist entries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "waitlist-api"
    }
