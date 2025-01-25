from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uvicorn
import asyncio
import logging
import os
from waitlist_service.db import init_db, get_database, waitlist_entries
from waitlist_service.models import WaitlistEntry
from databases import Database
from sqlalchemy.exc import IntegrityError

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
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Get database dependency
async def get_db():
    database = await get_database()
    if not database:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return database

# Models
class WaitlistEntryCreate(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    name: str = Field(..., description="Name of the user")  # Make name required
    comment: Optional[str] = Field(None, description="Additional comments")
    referral_source: Optional[str] = Field(None, description="Source of referral")

class WaitlistEntryResponse(BaseModel):
    id: int
    email: str
    name: str
    comment: Optional[str]
    referral_source: Optional[str]
    created_at: datetime
    is_active: bool

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Waitlist Service API"}

@app.post("/waitlist", response_model=WaitlistEntryResponse)
async def add_to_waitlist(entry: WaitlistEntryCreate, db: Database = Depends(get_db)):
    """
    Add a new entry to the waitlist
    
    Parameters:
    - email: Required email address
    - name: Required user name
    - comment: Optional additional comments
    - referral_source: Optional referral source
    
    Returns:
    - The created waitlist entry with timestamp
    """
    try:
        # Check for existing email first
        query = waitlist_entries.select().where(waitlist_entries.c.email == entry.email)
        existing = await db.fetch_one(query)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Email {entry.email} is already registered"
            )
            
        # Insert new entry
        query = waitlist_entries.insert().values(
            email=entry.email,
            name=entry.name,
            comment=entry.comment,
            referral_source=entry.referral_source,
            is_active=True
        )
        last_record_id = await db.execute(query)
        
        # Fetch the created entry
        query = waitlist_entries.select().where(waitlist_entries.c.id == last_record_id)
        result = await db.fetch_one(query)
        
        logger.info(f"Created waitlist entry for email: {entry.email}")
        return dict(result)
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error adding waitlist entry: {str(e)}")
        raise HTTPException(status_code=409, detail="Email already registered")
    except Exception as e:
        logger.error(f"Error adding waitlist entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/waitlist", response_model=List[WaitlistEntryResponse])
async def get_all_entries(db: Database = Depends(get_db)):
    """
    Get all waitlist entries
    """
    try:
        query = waitlist_entries.select()
        results = await db.fetch_all(query)
        return [dict(row) for row in results]
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
