from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import get_db_settings
from .models import Base
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.settings = get_db_settings()
        self.engine = None
        self.SessionLocal = None
        
    async def init_db(self):
        """Initialize database connection"""
        try:
            db_url = None
            
            if self.settings.DB_TYPE == "sqlite":
                # Ensure the data directory exists
                db_dir = os.path.dirname(self.settings.SQLITE_URL.replace('sqlite:///', ''))
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                db_url = self.settings.SQLITE_URL
                connect_args = {"check_same_thread": False}
            elif self.settings.DB_TYPE == "postgres" and self.settings.POSTGRES_URL:
                db_url = self.settings.POSTGRES_URL
                connect_args = {}
            else:
                logger.warning(f"Unsupported or unconfigured database type: {self.settings.DB_TYPE}, falling back to SQLite")
                db_url = "sqlite:///./waitlist.db"
                connect_args = {"check_same_thread": False}
            
            # Create engine
            self.engine = create_engine(
                db_url,
                connect_args=connect_args
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database initialized with {self.settings.DB_TYPE} at {db_url}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def get_db(self):
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Create global database instance
db = Database()
