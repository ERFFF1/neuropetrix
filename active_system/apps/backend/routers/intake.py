from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

router = APIRouter(prefix="/intake", tags=["Patient Intake"])

class HBYSData(BaseModel):
    ECOG: Optional[int] = None
    eGFR: Optional[float] = None
    BloodGlucose_mgdl: Optional[float] = None
    allergies: List[str] = []
    meds: List[str] = []
    additional_data: Optional[Dict[str, Any]] = None

class PatientPacket(BaseModel):
    patient_id: str
    icd10: str
    clinical_goal: str  # staging, response, lymphoma_followup
    hbys: HBYSData
    intake_timestamp: Optional[datetime] = None
    source_system: Optional[str] = "HBYS"

@router.post("/patient")
async def intake_patient(patient_packet: PatientPacket):
    """
    HBYS'den hasta verisi alıp sisteme kaydet
    """
    try:
        # Timestamp ekle
        if not patient_packet.intake_timestamp:
            patient_packet.intake_timestamp = datetime.now()
        
        # Validation
        if patient_packet.clinical_goal not in ["staging", "response", "lymphoma_followup"]:
            raise HTTPException(
                status_code=400, 
                detail="clinical_goal must be one of: staging, response, lymphoma_followup"
            )
        
        # Dosyaya kaydet (production'da database kullanılır)
        case_dir = f"data/cases/{patient_packet.patient_id}"
        os.makedirs(case_dir, exist_ok=True)
        
        case_file = f"{case_dir}/patient_packet.json"
        with open(case_file, "w") as f:
            json.dump(patient_packet.dict(), f, default=str, indent=2)
        
        # Case meta oluştur
        case_meta = {
            "patient_id": patient_packet.patient_id,
            "icd10": patient_packet.icd10,
            "clinical_goal": patient_packet.clinical_goal,
            "intake_timestamp": patient_packet.intake_timestamp.isoformat(),
            "status": "intake_completed",
            "imaging_available": False,
            "evidence_built": False,
            "report_generated": False
        }
        
        meta_file = f"{case_dir}/case_meta.json"
        with open(meta_file, "w") as f:
            json.dump(case_meta, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Patient {patient_packet.patient_id} intake completed",
            "case_id": patient_packet.patient_id,
            "clinical_goal": patient_packet.clinical_goal,
            "next_steps": ["evidence_build", "imaging_upload_optional"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intake failed: {str(e)}")

@router.get("/patient/{patient_id}")
async def get_patient_status(patient_id: str):
    """
    Hasta durumunu kontrol et
    """
    try:
        case_dir = f"data/cases/{patient_id}"
        meta_file = f"{case_dir}/case_meta.json"
        
        if not os.path.exists(meta_file):
            raise HTTPException(status_code=404, detail="Patient not found")
        
        with open(meta_file, "r") as f:
            case_meta = json.load(f)
        
        return case_meta
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patient status: {str(e)}")

@router.get("/all-patients")
async def list_patients():
    """
    Tüm hastaları listele
    """
    try:
        cases_dir = "data/cases"
        if not os.path.exists(cases_dir):
            return {"patients": []}
        
        patients = []
        for case_dir in os.listdir(cases_dir):
            meta_file = f"{cases_dir}/{case_dir}/case_meta.json"
            if os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    case_meta = json.load(f)
                    patients.append(case_meta)
        
        return {"patients": patients}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list patients: {str(e)}")
