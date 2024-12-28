from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create SQLAlchemy base class
Base = declarative_base()

def get_supabase_client() -> Client:
    """Get Supabase client for database operations."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
    
    return create_client(supabase_url, supabase_key)

def get_database_url():
    """Get database URL based on environment."""
    if os.getenv("ENVIRONMENT") == "production":
        database_url = os.getenv("SUPABASE_DATABASE_URL")
        if not database_url:
            raise ValueError("SUPABASE_DATABASE_URL environment variable not set")
        return database_url.replace("?sslmode=require", "")
    else:
        # Development: Use SQLite
        return "sqlite+aiosqlite:///data/development.db"

def create_engine_with_config():
    """Create SQLAlchemy engine with appropriate configuration."""
    database_url = get_database_url()
    
    if os.getenv("ENVIRONMENT") == "production":
        return create_async_engine(
            database_url,
            connect_args={"ssl": "require"}
        )
    else:
        return create_async_engine(database_url)
