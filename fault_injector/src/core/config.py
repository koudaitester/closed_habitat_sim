from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WORLD_STATE_URL: str = "http://127.0.0.1:8000"
    SERVICE_NAME: str = "fault_injector"

settings = Settings()
