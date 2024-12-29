# backend/database/db_state.py

from pathlib import Path
import logging
import os
from dotenv import load_dotenv
import databases
import sqlalchemy
import ssl
from .models import WaitlistEntry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Load Environment Variables ===
load_dotenv()

# === Database Configuration ===
# Get environment
ENV = os.getenv("ENVIRONMENT", "development")
logger.info(f"Running in {ENV} environment")

# Initialize database variable
database = None

# Database configuration based on environment
if ENV == "production":
    # Production: Use Supabase PostgreSQL
    DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("SUPABASE_DATABASE_URL is required in production environment")
    
    logger.info("Initializing Supabase PostgreSQL database connection")
    
    # Create SSL context for Supabase
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    
    # Get SSL mode from environment variable, default to 'require'
    ssl_mode = os.getenv("SUPABASE_SSL_MODE", "require")
    
    if ssl_mode == "disable":
        logger.warning("SSL verification disabled by configuration")
        ssl_context.verify_mode = ssl.CERT_NONE
    elif ssl_mode == "require":
        logger.info("Using SSL in require mode (no certificate verification)")
        ssl_context.verify_mode = ssl.CERT_NONE
    else:  # verify-full
        # Try to load the Supabase certificate if it exists
        cert_paths = [
            Path("./certificates/supabase.crt").resolve(),
            Path(os.getenv("SUPABASE_CA_CERT_PATH", "")).resolve(),
            Path.home() / ".postgresql" / "root.crt"
        ]
        
        cert_loaded = False
        for cert_path in cert_paths:
            if cert_path.exists():
                logger.info(f"Loading Supabase certificate from {cert_path}")
                ssl_context.load_verify_locations(cafile=str(cert_path))
                cert_loaded = True
                break
        
        if not cert_loaded:
            logger.warning("No valid certificate found, falling back to require mode")
            ssl_context.verify_mode = ssl.CERT_NONE
    
    # Initialize database with SSL context
    database = databases.Database(
        DATABASE_URL,
        ssl=ssl_context,
        min_size=1,
        max_size=5
    )
    logger.info("Supabase PostgreSQL database initialized")

else:
    # Development: Use local SQLite database
    logger.info("Running in development mode with SQLite database")
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "./data/development.db")).resolve()
    
    # Ensure the directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Database directory ensured at: {DATABASE_PATH.parent}")
    
    # Create the SQLite URL with aiosqlite
    DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    logger.info(f"Using SQLite database at: {DATABASE_PATH}")
    
    # Initialize database connection
    database = databases.Database(DATABASE_URL)
    
    # Create tables in development (SQLite only)
    sync_url = f"sqlite:///{DATABASE_PATH}"
    engine = sqlalchemy.create_engine(sync_url)
    WaitlistEntry.metadata.create_all(engine)
    logger.info("Development database tables created")

if database is None:
    raise RuntimeError("Database failed to initialize")

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
        database = databases.Database(database_url)
