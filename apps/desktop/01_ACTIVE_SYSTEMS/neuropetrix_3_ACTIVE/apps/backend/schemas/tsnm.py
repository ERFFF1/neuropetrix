from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TSNMRequest(BaseModel):
    patient_id: str
    modality: str = "FDG"
    device_model: str
    fdg_dose_mbq: float
    glycemia_mgdl: float
    fasting_hours: int
    findings: str
    conclusion: str

class TSNMResponse(BaseModel):
    success: bool
    report_id: str
    report_content: str
    generated_at: str




