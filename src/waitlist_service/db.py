#!/usr/bin/env python3
import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, text
from sqlalchemy.sql import func
from databases import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
database = None
metadata = MetaData()

# Define tables
waitlist_entries = Table(
    "waitlist_entries",  # Match the model's table name
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, nullable=False),
    Column("email", String, unique=True, nullable=False, index=True),
    Column("ip_address", String, nullable=True),
    Column("comment", String, nullable=True),
    Column("referral_source", String, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("is_active", Boolean, server_default=text('true'))
)

async def get_database():
    """Get the database instance."""
    return database

async def init_db():
    """Initialize the database connection and create tables."""
    global database
    
    try:
        # Set up SQLite database path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        instance_dir = os.path.join(script_dir, '..', '..', 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        
        # Get database URL from environment or use SQLite
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            db_path = os.path.join(instance_dir, 'waitlist.db')
            database_url = f"sqlite+aiosqlite:///{db_path}"
        
        logger.info(f"Initializing database connection to {database_url}")
        
        # Convert synchronous PostgreSQL URL to async if needed
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
            engine_args = {
                'echo': True,
                'pool_pre_ping': True,
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_recycle': 1800
            }
        else:
            # SQLite configuration
            if database_url.startswith('sqlite://'):
                database_url = database_url.replace('sqlite://', 'sqlite+aiosqlite://')
            engine_args = {
                'echo': True,
                'pool_pre_ping': True
            }
        
        # Create engine with appropriate configuration
        engine = create_async_engine(database_url, **engine_args)
        
        # Create database instance
        database = Database(database_url)
        await database.connect()
        
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
        database = None

if __name__ == "__main__":
    asyncio.run(init_db())
