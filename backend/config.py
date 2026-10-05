from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkyGuard AI Backend"
    VERSION: str = "3.0.0"
    DEFAULT_STATION_ID: str = "AGRA-01"
    DATABASE_PATH: str = "skyguard.db"
    
    # OpenRouter API configurations
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
