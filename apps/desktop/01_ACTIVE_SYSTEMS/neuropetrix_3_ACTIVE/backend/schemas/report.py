from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ReportRequest(BaseModel):
    patient: Dict[str, Any]
    report_type: str = "standard"
    findings: Optional[str] = None
    conclusion: Optional[str] = None

class ReportResponse(BaseModel):
    success: bool
    report: str
    format: str
    generated_at: str

class TSNMReport(BaseModel):
    modality: str
    device_model: str
    fdg_dose_mbq: float
    glycemia_mgdl: float
    fasting_hours: int
    findings: str
    conclusion: str
    recommendations: List[str]




