from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkyGuard AI - AWS Anomaly Detection Engine"
    API_V1_STR: str = "/api/v1"
    STATION_ID: str = "AGRA-01"
    STATION_NAME: str = "Agra Central Agro-Met Station"
    LATITUDE: float = 27.1767
    LONGITUDE: float = 78.0081
    ELEVATION_M: float = 169.0
    
    # Ingestion & Windowing
    SAMPLING_INTERVAL_SEC: float = 1.0
    WINDOW_SIZE: int = 12
    RECONSTRUCTION_THRESHOLD: float = 0.042
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "*"
    ]

    class Config:
        case_sensitive = True

settings = Settings()
