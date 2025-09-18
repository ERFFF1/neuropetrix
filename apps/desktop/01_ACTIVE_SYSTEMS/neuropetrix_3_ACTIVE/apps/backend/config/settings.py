"""
Settings configuration for NeuroPETRIX v2.0
Environment variables and configuration management
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "NeuroPETRIX v2.0"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    
    # Database
    database_url: str = Field(
        default="postgresql://user:pass@localhost:5432/neuro_db",
        env="DB_URL"
    )
    
    # FHIR Integration
    fhir_base_url: str = Field(
        default="http://localhost:8081/fhir",
        env="FHIR_BASE_URL"
    )
    fhir_username: Optional[str] = Field(default=None, env="FHIR_USER")
    fhir_password: Optional[str] = Field(default=None, env="FHIR_PASS")
    fhir_timeout: int = Field(default=30, env="FHIR_TIMEOUT")
    
    # Models and AI
    models_path: str = Field(
        default="./models/monai",
        env="MODELS_PATH"
    )
    ai_timeout: int = Field(default=300, env="AI_TIMEOUT")  # 5 minutes
    
    # DICOM and Imaging
    dicom_temp_dir: str = Field(
        default="./temp/dicom",
        env="DICOM_TEMP_DIR"
    )
    max_dicom_size: int = Field(
        default=1024 * 1024 * 100,  # 100MB
        env="MAX_DICOM_SIZE"
    )
    
    # Orthanc (optional DICOM server)
    orthanc_url: Optional[str] = Field(default=None, env="ORTHANC_URL")
    orthanc_username: Optional[str] = Field(default=None, env="ORTHANC_USER")
    orthanc_password: Optional[str] = Field(default=None, env="ORTHANC_PASS")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # File Storage
    data_dir: str = Field(
        default="./data",
        env="DATA_DIR"
    )
    reports_dir: str = Field(
        default="./data/reports",
        env="REPORTS_DIR"
    )
    uploads_dir: str = Field(
        default="./data/uploads",
        env="UPLOADS_DIR"
    )
    
    # Compliance and Audit
    audit_enabled: bool = Field(default=True, env="AUDIT_ENABLED")
    audit_retention_days: int = Field(default=365, env="AUDIT_RETENTION_DAYS")
    model_registry_path: str = Field(
        default="./compliance/model_registry.json",
        env="MODEL_REGISTRY_PATH"
    )
    
    # Performance
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    worker_timeout: int = Field(default=600, env="WORKER_TIMEOUT")  # 10 minutes
    
    # External Services
    pubmed_api_key: Optional[str] = Field(default=None, env="PUBMED_API_KEY")
    embase_api_key: Optional[str] = Field(default=None, env="EMBASE_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.data_dir,
            self.reports_dir,
            self.uploads_dir,
            self.dicom_temp_dir,
            os.path.dirname(self.model_registry_path)
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.database_url,
            "echo": self.debug,
            "pool_size": self.max_workers,
            "max_overflow": 10
        }
    
    @property
    def fhir_config(self) -> Dict[str, Any]:
        """Get FHIR configuration"""
        config = {
            "base_url": self.fhir_base_url,
            "timeout": self.fhir_timeout
        }
        
        if self.fhir_username and self.fhir_password:
            config.update({
                "username": self.fhir_username,
                "password": self.fhir_password
            })
        
        return config
    
    @property
    def orthanc_config(self) -> Optional[Dict[str, Any]]:
        """Get Orthanc configuration if available"""
        if not all([self.orthanc_url, self.orthanc_username, self.orthanc_password]):
            return None
        
        return {
            "url": self.orthanc_url,
            "username": self.orthanc_username,
            "password": self.orthanc_password
        }
    
    def validate(self) -> bool:
        """Validate critical settings"""
        errors = []
        
        # Check required directories
        if not os.path.exists(self.models_path):
            errors.append(f"Models path does not exist: {self.models_path}")
        
        # Check database URL format
        if not self.database_url.startswith(("postgresql://", "sqlite://")):
            errors.append("Invalid database URL format")
        
        # Check FHIR URL format
        if not self.fhir_base_url.startswith(("http://", "https://")):
            errors.append("Invalid FHIR base URL format")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get settings instance"""
    return settings

def reload_settings():
    """Reload settings from environment"""
    global settings
    settings = Settings()
    return settings
