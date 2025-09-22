from fastapi import APIRouter
import sys
import os

router = APIRouter()

@router.get("/health")
def legacy_health():
    return {
        "status": "ok", 
        "source": "legacy", 
        "streamlit": "available",
        "features": ["clinical-decision", "dicom", "reports"]
    }

@router.post("/clinical-decision")
def legacy_clinical_decision(payload: dict):
    # Eski Streamlit sistemindeki clinical decision logic'i buraya adapte et
    return {
        "status": "processed", 
        "source": "legacy", 
        "result": "mock",
        "payload": payload
    }

@router.get("/streamlit-status")
def streamlit_status():
    return {
        "status": "available",
        "port": 8501,
        "url": "http://localhost:8501"
    }
