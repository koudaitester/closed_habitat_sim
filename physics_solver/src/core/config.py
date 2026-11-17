# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WORLD_STATE_URL: str = "http://127.0.0.1:8000"
    TICK_INTERVAL_SEC: float = 1.0
    LOG_LEVEL: str = "INFO"

settings = Settings()
