from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "NeuroPETRIX - Complete AI System"
    API_VERSION: str = "1.5.0"
    API_BASE: str = "http://127.0.0.1:8000"
    
    # AI Configuration
    MOCK_AI: bool = True
    MONAI_ENABLED: bool = True
    PYRADIOMICS_ENABLED: bool = True
    GEMINI_API_KEY: Optional[str] = None
    
    # CORS
    ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173", 
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///neuropetrix.db"
    
    # External Services
    FHIR_URL: Optional[str] = None
    ORTHANC_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Performance & Monitoring
    LOG_LEVEL: str = "INFO"
    CACHE_TTL: int = 300
    PERFORMANCE_MONITORING: bool = True
    
    # Security
    SECRET_KEY: Optional[str] = None
    
    # Development
    DEBUG: bool = True
    RELOAD: bool = True
    WORKERS: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Extra field'ları ignore et

settings = Settings()


