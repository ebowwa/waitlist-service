from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from urllib.parse import urlparse, quote_plus

Base = declarative_base()

def get_supabase_client() -> Client:
    """Get Supabase client using environment variables."""
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        
    return create_client(supabase_url, supabase_key)

def init_db(database_url: str = None):
    """Initialize database with the given URL."""
    # If no URL provided, default to SQLite
    if not database_url:
        database_url = "sqlite:///instance/waitlist.db"
    
    if database_url.startswith('sqlite'):
        if database_url == 'sqlite:///:memory:':
            engine = create_engine(database_url, connect_args={"check_same_thread": False})
        else:
            # For SQLite file-based, ensure the directory exists
            db_path = database_url.replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            engine = create_engine(database_url, connect_args={"check_same_thread": False})
            
        # Import models here to avoid circular imports
        from .models import WaitlistEntry  # noqa
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"Created tables: {Base.metadata.tables.keys()}")
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal
    else:
        # For PostgreSQL (Supabase), convert asyncpg URL to psycopg2 URL
        parsed = urlparse(database_url)
        # Extract username and password from netloc
        auth = parsed.netloc.split('@')[0]
        host_port = parsed.netloc.split('@')[1]
        username = auth.split(':')[0]
        password = auth.split(':')[1]
        
        # Construct the new URL with quoted password
        sync_url = f"postgresql://{username}:{quote_plus(password)}@{host_port}{parsed.path}?{parsed.query}"
        engine = create_engine(sync_url)
        
        # Import models here to avoid circular imports
        from .models import WaitlistEntry  # noqa
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"Created tables: {Base.metadata.tables.keys()}")
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal
