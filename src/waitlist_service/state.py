"""
Global state management for the waitlist service
"""
import os
import logging
import ssl
from typing import Optional
import certifi
from databases import Database
from dotenv import load_dotenv
from .models import WaitlistEntry

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Environment configuration
ENV = os.getenv("ENV", "development")
logger.info(f"Running in {ENV} environment")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Configure SSL context for database
ssl_context = ssl.create_default_context(cafile=certifi.where())
if ENV == "development":
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    logger.warning("SSL certificate verification disabled in development mode")

# Initialize database with SSL context
database = Database(
    DATABASE_URL,
    ssl=ssl_context,
    min_size=5,
    max_size=20
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Only enforce Supabase config in production
if ENV == "production" and not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Supabase configuration incomplete. Check environment variables.")
elif ENV == "development":
    logger.warning("Running in development mode - Supabase integration disabled")

logger.info("Initializing database connection")

try:
    # Initialize Supabase client here if needed
    pass
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

logger.info("Database connection initialized")

def get_db_state():
    """Get the current database state."""
    return {
        "database": database,
        "metadata": WaitlistEntry.metadata,
        "environment": ENV,
        "url": DATABASE_URL
    }

def set_db_state(database_url: str = None):
    """Set the database state with a new URL."""
    global database
    if database_url:
        database = Database(database_url)
    return database
