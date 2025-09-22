from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Patient(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    diagnosis: Optional[str] = None
    icd_codes: List[str] = []
    medications: List[str] = []
    comorbidities: List[str] = []
    clinical_goals: List[str] = []
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "P001",
                "name": "Ali Yılmaz",
                "age": 65,
                "gender": "M",
                "icd_codes": ["C34.9"],
                "clinical_goals": ["staging", "diagnosis"]
            }
        }
    }

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    diagnosis: Optional[str] = None
    icd_codes: List[str] = []
    clinical_goals: List[str] = []

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    icd_codes: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    comorbidities: Optional[List[str]] = None
    clinical_goals: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None


