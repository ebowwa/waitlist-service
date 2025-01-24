#!/usr/bin/env python3
import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, text
from sqlalchemy.sql import func
from databases import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
database = None
metadata = MetaData()

# Define tables
waitlist = Table(
    "waitlist",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("name", String),
    Column("ip_address", String),
    Column("comment", String),
    Column("referral_source", String),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now())
)

async def get_database():
    """Get the database instance."""
    return database

async def init_db():
    """Initialize the database connection and create tables."""
    global database
    
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
            
        logger.info(f"Initializing database connection to {database_url}")
        
        # Convert synchronous PostgreSQL URL to async if needed
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        # Create engine with connection pooling
        engine = create_async_engine(
            database_url,
            echo=True,  # Log all SQL
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections after 30 minutes
        )
        
        # Create database instance
        database = Database(database_url)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            
        logger.info("Database initialized successfully")
        return database
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

async def close_db():
    """Close database connection."""
    global database
    if database:
        await database.disconnect()
        logger.info("Database connection closed")

if __name__ == "__main__":
    asyncio.run(init_db())
