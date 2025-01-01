from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class DatabaseSettings(BaseSettings):
    # SQLite settings
    SQLITE_URL: str = "sqlite:///./waitlist.db"
    
    # Supabase PostgreSQL settings (optional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    POSTGRES_URL: Optional[str] = None
    
    # Database type
    DB_TYPE: str = "sqlite"  # or "postgres"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings()
