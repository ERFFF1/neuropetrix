from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_TITLE: str = "NeuroPETRIX - Complete AI System"
    API_VERSION: str = "1.5.0"
    MOCK_AI: bool = True
    ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173", 
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ]
    FHIR_URL: str | None = None
    DATABASE_URL: str = "sqlite:///neuropetrix.db"
    LOG_LEVEL: str = "INFO"
    CACHE_TTL: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()


