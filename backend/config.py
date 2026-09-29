from pydantic_settings import BaseSettings, SettingsConfigDict
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

    # External MQTT edge ingestion. Disabled by default so the local simulator remains
    # the zero-setup development path.
    MQTT_ENABLED: bool = False
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_TOPIC: str = "skyguard/telemetry"
    MQTT_CLIENT_ID: str = "skyguard-backend"
    MQTT_QOS: int = 1
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "*"
    ]

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

settings = Settings()
