from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]
    type: str = "clinical"

@router.get("/health")
def v1_health():
    return {
        "status": "ok", 
        "source": "v1", 
        "features": ["ai", "dicom", "reports", "monitoring"]
    }

@router.post("/analyze")
def v1_analyze(request: AnalysisRequest):
    return {
        "status": "analyzed", 
        "source": "v1", 
        "result": "mock",
        "request_type": request.type,
        "data_keys": list(request.data.keys()) if request.data else []
    }

@router.get("/features")
def v1_features():
    return {
        "ai_models": ["gemini", "whisper", "monai"],
        "dicom_support": True,
        "report_generation": True,
        "real_time": True
    }
