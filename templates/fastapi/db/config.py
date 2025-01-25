from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class AppSettings(BaseSettings):
    """Base application settings"""
    APP_NAME: str = "Waitlist Service API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        extra = "allow"

class DatabaseSettings(BaseSettings):
    """Database-specific settings"""
    SQLITE_URL: str = "sqlite:///./waitlist.db"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    POSTGRES_URL: Optional[str] = None
    DB_TYPE: str = "sqlite"

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_app_settings() -> AppSettings:
    """Get cached application settings"""
    return AppSettings()

@lru_cache()
def get_db_settings() -> DatabaseSettings:
    """Get cached database settings"""
    return DatabaseSettings()

# How this configuration works:
# 1. We define two Pydantic BaseSettings classes: AppSettings and DatabaseSettings.
# 2. These classes automatically load values from environment variables or .env file.
# 3. Default values are provided for each setting.
# 4. The @lru_cache decorator is used to cache the settings, improving performance.
# 5. To use these settings:
#    - Import get_app_settings() or get_db_settings()
#    - Call the function to get the respective settings object
#    - Access settings as attributes, e.g., get_app_settings().APP_NAME
# 6. The configuration supports both SQLite and PostgreSQL databases.
# 7. The DB_TYPE setting determines which database is used in the application.
