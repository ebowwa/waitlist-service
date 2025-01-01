from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import get_db_settings
from .models import Base
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.settings = get_db_settings()
        self.engine = None
        self.SessionLocal = None
        
    async def init_db(self):
        """Initialize database connection"""
        try:
            if self.settings.DB_TYPE == "sqlite":
                # SQLite connection
                self.engine = create_engine(
                    self.settings.SQLITE_URL,
                    connect_args={"check_same_thread": False}
                )
            elif self.settings.DB_TYPE == "postgres" and self.settings.POSTGRES_URL:
                # PostgreSQL connection
                self.engine = create_engine(self.settings.POSTGRES_URL)
            else:
                raise ValueError(f"Unsupported database type: {self.settings.DB_TYPE}")
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database initialized with {self.settings.DB_TYPE}")
            
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
