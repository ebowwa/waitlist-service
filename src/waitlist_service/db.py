#!/usr/bin/env python3
import os
import asyncio
from pathlib import Path
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database connection
database = None
metadata = None

async def init_db():
    """Initialize the database tables."""
    try:
        global database, metadata
        
        # Get environment and database URL
        env = os.getenv("ENVIRONMENT", "development")
        database_url = os.getenv("DATABASE_URL")
        
        logger.info(f"Initializing database in {env} environment")
        
        if env == "development" and not database_url:
            # Development: Use SQLite if no DATABASE_URL is provided
            logger.info("Using SQLite database for development")
            BASE_DIR = Path(__file__).resolve().parent.parent / "data"
            DATABASE_NAME = "development.db"
            DATABASE_PATH = BASE_DIR / DATABASE_NAME
            
            # Ensure the data directory exists
            BASE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create SQLite engine
            engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_PATH}")
            
        else:
            # Production or custom DATABASE_URL: Use PostgreSQL
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is required")
                
            logger.info("Using PostgreSQL database")
            
            # Convert synchronous PostgreSQL URL to async
            if database_url.startswith('postgresql://'):
                database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
            
            # Create PostgreSQL engine
            engine = create_async_engine(
                database_url,
                echo=True,  # Log all SQL statements
                pool_size=5,
                max_overflow=10
            )
        
        # Initialize tables
        metadata = sqlalchemy.MetaData()
        
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            
        logger.info("Database initialization complete")
        
        return engine
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
