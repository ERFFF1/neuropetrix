from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    system: Dict[str, Any]
    services: Dict[str, str]

class VersionResponse(BaseModel):
    version: str
    build_date: str
    features: List[str]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None




