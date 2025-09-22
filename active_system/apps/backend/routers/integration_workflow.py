"""NeuroPETRIX Integration Workflow Router (staging/diagnosis/followup)"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging, uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration")

router = APIRouter(prefix="/integration/workflow", tags=["integration-workflow"])

class StartPayload(BaseModel):
    patient_id: Optional[str] = None
    purpose: str = "staging"
    icd_code: Optional[str] = None
    case_meta: Optional[Dict[str, Any]] = None

@router.get("/health")
def health():
    return {"status": "OK", "router": "integration_workflow"}

try:
    from backend.services.jobs import enqueue, get
    from backend.database_workflow import workflow_db
except ImportError:
    from services.jobs import enqueue, get
    from database_workflow import workflow_db

def heavy_work(case_id: str, payload: dict):
    """Ağır iş simülasyonu"""
    import time
    time.sleep(2)  # simulate heavy processing
    return {
        "case_id": case_id,
        "summary": "Workflow completed successfully",
        "steps": ["PICO", "MONAI", "Evidence", "Decision", "Report"],
        "payload": payload
    }

@router.post("/start")
def start_workflow(payload: StartPayload, tasks: BackgroundTasks):
    try:
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        logger.info("Workflow start | case_id=%s | payload=%s", case_id, payload.model_dump())
        
        # Database'e case oluştur
        workflow_db.create_case(
            case_id=case_id,
            patient_id=payload.patient_id,
            purpose=payload.purpose,
            icd_code=payload.icd_code,
            metadata=payload.case_meta
        )
        
        # Ağır işi kuyruğa al
        job_id = enqueue(heavy_work, case_id, payload.model_dump())
        
        # Job'u database'e kaydet
        workflow_db.add_job(job_id, case_id, "heavy_work", "queued")
        
        return {
            "ok": True,
            "case_id": case_id,
            "job_id": job_id,
            "workflow": {
                "case_id": case_id,
                "started_at": datetime.utcnow().isoformat() + "Z",
                "patient_id": payload.patient_id,
                "purpose": payload.purpose,
                "icd_code": payload.icd_code,
                "status": "queued"
            }
        }
    except Exception as e:
        logger.exception("integration workflow error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job/{job_id}")
def get_job_status(job_id: str):
    """Job durumunu kontrol et"""
    return get(job_id)

@router.get("/status/{case_id}")
def get_workflow_status(case_id: str):
    """Workflow durumunu kontrol et"""
    try:
        # Database'den case bilgilerini çek
        case = workflow_db.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Workflow steps'leri çek
        steps = workflow_db.get_workflow_steps(case_id)
        
        # Progress hesapla
        completed_steps = len([s for s in steps if s["status"] == "completed"])
        total_steps = 5  # PICO, MONAI, Evidence, Decision, Report
        progress = int((completed_steps / total_steps) * 100)
        
        status = {
            "case_id": case_id,
            "patient_id": case["patient_id"],
            "purpose": case["purpose"],
            "icd_code": case["icd_code"],
            "current_step": steps[-1]["step_name"] if steps else "workflow_started",
            "overall_progress": progress,
            "status": case["status"],
            "steps": steps,
            "created_at": case["created_at"],
            "updated_at": case["updated_at"]
        }
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Status check failed")
        raise HTTPException(status_code=500, detail=str(e))

class PicoMonaiPayload(BaseModel):
    case_id: str
    patient_data: Optional[Dict[str, Any]] = None

@router.post("/pico-monai")
def execute_pico_monai_integration(payload: PicoMonaiPayload, tasks: BackgroundTasks):
    """PICO-MONAI entegrasyonu"""
    try:
        logger.info("PICO-MONAI integration started | case_id=%s", payload.case_id)
        # Mock integration - gerçek implementasyonda AI pipeline tetiklenecek
        result = {
            "status": "mock", 
            "message": "Mock integration service",
            "pico_question": "What is the diagnostic accuracy of PET/CT for staging?",
            "monai_segmentation": "mock_segmentation_result"
        }
        return {
            "success": True, 
            "case_id": payload.case_id, 
            "integration_result": result
        }
    except Exception as e:
        logger.exception("PICO-MONAI integration failed")
        raise HTTPException(status_code=500, detail=str(e))

class EvidencePayload(BaseModel):
    case_id: str
    evidence_type: str = "literature_review"

@router.post("/evidence")
def execute_evidence_analysis(payload: EvidencePayload, tasks: BackgroundTasks):
    """Evidence analizi"""
    try:
        logger.info("Evidence analysis started | case_id=%s", payload.case_id)
        # Mock evidence analysis - gerçek implementasyonda literature search yapılacak
        result = {
            "literature_review": True,
            "clinical_guidelines": ["NCCN", "ESMO", "ASCO"],
            "evidence_level": "B",
            "papers_found": 47,
            "grade_quality": "Moderate"
        }
        return {
            "success": True, 
            "case_id": payload.case_id, 
            "evidence_result": result
        }
    except Exception as e:
        logger.exception("Evidence analysis failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decision")
def execute_decision_composition(case_id: str, tasks: BackgroundTasks):
    """Karar kompozisyonu"""
    try:
        logger.info("Decision composition started | case_id=%s", case_id)
        # Mock decision - gerçek implementasyonda AI decision support kullanılacak
        result = {
            "status": "mock", 
            "message": "Mock decision service",
            "clinical_decision": "Proceed with staging",
            "confidence_score": 0.85,
            "recommendations": ["Complete staging", "Consider biopsy"]
        }
        return {
            "success": True, 
            "case_id": case_id, 
            "decision_result": result
        }
    except Exception as e:
        logger.exception("Decision composition failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
def execute_report_generation(case_id: str, tasks: BackgroundTasks):
    """Rapor üretimi"""
    try:
        logger.info("Report generation started | case_id=%s", case_id)
        # Mock report - gerçek implementasyonda TSNM formatında rapor üretilecek
        result = {
            "report_type": "TSNM",
            "sections": [
                "Clinical Summary", 
                "Imaging Findings", 
                "SUV Analysis",
                "Recommendations"
            ],
            "status": "completed",
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        return {
            "success": True, 
            "case_id": case_id, 
            "report_result": result
        }
    except Exception as e:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
def execute_complete_workflow(payload: Dict[str, Any], tasks: BackgroundTasks):
    """Tam workflow yürütme"""
    try:
        logger.info("Complete workflow started")
        case_id = f"CASE-{uuid.uuid4()}"
        
        # Mock complete workflow - gerçek implementasyonda tüm adımlar sırayla çalışacak
        result = {
            "success": True,
            "case_id": case_id,
            "workflow_completed": True,
            "all_steps": [
                "start", 
                "pico-monai", 
                "evidence", 
                "decision", 
                "report"
            ],
            "completion_time": datetime.utcnow().isoformat() + "Z",
            "total_duration": "mock_duration"
        }
        return result
    except Exception as e:
        logger.exception("Complete workflow failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cases")
def get_all_cases(limit: int = 100):
    """Tüm case'leri listele"""
    try:
        cases = workflow_db.get_all_cases(limit)
        return {
            "cases": cases,
            "total": len(cases),
            "limit": limit
        }
    except Exception as e:
        logger.exception("Error getting cases")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}")
def get_case_details(case_id: str):
    """Case detaylarını getir"""
    try:
        case = workflow_db.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        steps = workflow_db.get_workflow_steps(case_id)
        case["steps"] = steps
        
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting case details")
        raise HTTPException(status_code=500, detail=str(e))

