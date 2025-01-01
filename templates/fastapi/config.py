import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Waitlist Service API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("SUPABASE_DATABASE_URL", "sqlite+aiosqlite:///data/development.db")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
