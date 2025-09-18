from fastapi import APIRouter, HTTPException
import requests
import os
try:
    from backend.utils.fhir_builder import diagnostic_report, create_workflow_bundle
except ImportError:
    from utils.fhir_builder import diagnostic_report, create_workflow_bundle
try:
    from backend.core.settings import settings
except ImportError:
    from core.settings import settings

router = APIRouter(prefix="/fhir", tags=["fhir"])

@router.post("/send-report/{patient_id}")
def send_report(patient_id: str, text: str):
    """Diagnostic report'u FHIR server'a gönder"""
    base = settings.FHIR_URL
    if not base:
        raise HTTPException(400, "FHIR_URL not set in environment")
    
    try:
        payload = diagnostic_report(patient_id, text)
        r = requests.post(
            f"{base}/DiagnosticReport", 
            json=payload, 
            timeout=10,
            headers={"Content-Type": "application/fhir+json"}
        )
        
        if r.ok:
            return {
                "status": "success",
                "fhir_status": r.status_code,
                "patient_id": patient_id,
                "fhir_id": r.json().get("id") if r.json() else None
            }
        else:
            return {
                "status": "failed",
                "fhir_status": r.status_code,
                "error": r.text,
                "patient_id": patient_id
            }
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(500, f"FHIR server connection failed: {str(e)}")

@router.post("/send-workflow-bundle/{case_id}")
def send_workflow_bundle(case_id: str, workflow_data: dict):
    """Workflow bundle'ı FHIR server'a gönder"""
    base = settings.FHIR_URL
    if not base:
        raise HTTPException(400, "FHIR_URL not set in environment")
    
    try:
        # Mock patient_id - gerçek implementasyonda case'den çekilecek
        patient_id = workflow_data.get("patient_id", "UNKNOWN")
        
        bundle = create_workflow_bundle(patient_id, case_id, workflow_data)
        r = requests.post(
            f"{base}/Bundle", 
            json=bundle, 
            timeout=15,
            headers={"Content-Type": "application/fhir+json"}
        )
        
        if r.ok:
            return {
                "status": "success",
                "fhir_status": r.status_code,
                "case_id": case_id,
                "bundle_sent": True
            }
        else:
            return {
                "status": "failed",
                "fhir_status": r.status_code,
                "error": r.text,
                "case_id": case_id
            }
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(500, f"FHIR server connection failed: {str(e)}")

@router.get("/health")
def fhir_health():
    """FHIR connection health check"""
    base = settings.FHIR_URL
    if not base:
        return {"status": "disabled", "reason": "FHIR_URL not set"}
    
    try:
        r = requests.get(f"{base}/metadata", timeout=5)
        if r.ok:
            return {"status": "connected", "fhir_server": base}
        else:
            return {"status": "error", "fhir_server": base, "status_code": r.status_code}
    except:
        return {"status": "unreachable", "fhir_server": base}

