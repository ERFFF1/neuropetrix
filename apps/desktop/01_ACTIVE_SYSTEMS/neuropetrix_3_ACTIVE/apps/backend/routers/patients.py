from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
from pydantic import BaseModel

router = APIRouter(prefix="/patients", tags=["patients"])

class PatientData(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    gender: str
    diagnosis: str
    icd_codes: List[str]
    medications: List[str]
    comorbidities: List[str]
    clinical_goals: List[str]
    created_at: Optional[datetime] = None

class PatientCase(BaseModel):
    patient_id: str
    case_type: str  # 'initial', 'followup', 'comparison'
    clinical_context: str
    imaging_data: Optional[Dict[str, Any]] = None
    lab_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

def get_db():
    return sqlite3.connect("neuropetrix.db")

@router.post("/")
async def create_patient(patient: PatientData):
    """Yeni hasta kaydı oluştur"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO patients (id, name, age, gender, diagnosis, icd_codes, 
                                medications, comorbidities, clinical_goals, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id, patient.name, patient.age, patient.gender, patient.diagnosis,
            ','.join(patient.icd_codes), ','.join(patient.medications),
            ','.join(patient.comorbidities), ','.join(patient.clinical_goals),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return {"patient_id": patient_id, "message": "Hasta başarıyla oluşturuldu"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hasta oluşturma hatası: {str(e)}")

@router.get("/")
async def get_patients():
    """Tüm hastaları listele"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
        patients = cursor.fetchall()
        
        conn.close()
        
        return [{
            "id": p[0], "name": p[1], "age": p[2], "gender": p[3],
            "diagnosis": p[4], "icd_codes": p[5].split(',') if p[5] else [],
            "medications": p[6].split(',') if p[6] else [],
            "comorbidities": p[7].split(',') if p[7] else [],
            "clinical_goals": p[8].split(',') if p[8] else [],
            "created_at": p[9]
        } for p in patients]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hasta listesi hatası: {str(e)}")

@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    """Belirli bir hastayı getir"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        conn.close()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Hasta bulunamadı")
        
        return {
            "id": patient[0], "name": patient[1], "age": patient[2], "gender": patient[3],
            "diagnosis": patient[4], "icd_codes": patient[5].split(',') if patient[5] else [],
            "medications": patient[6].split(',') if patient[6] else [],
            "comorbidities": patient[7].split(',') if patient[7] else [],
            "clinical_goals": patient[8].split(',') if patient[8] else [],
            "created_at": patient[9]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hasta getirme hatası: {str(e)}")

@router.post("/{patient_id}/cases")
async def create_case(patient_id: str, case: PatientCase):
    """Hasta için yeni vaka oluştur"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        case_id = f"C{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO patient_cases (id, patient_id, case_type, clinical_context,
                                     imaging_data, lab_data, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id, patient_id, case.case_type, case.clinical_context,
            str(case.imaging_data) if case.imaging_data else None,
            str(case.lab_data) if case.lab_data else None,
            case.notes, datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return {"case_id": case_id, "message": "Vaka başarıyla oluşturuldu"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vaka oluşturma hatası: {str(e)}")

@router.get("/{patient_id}/cases")
async def get_patient_cases(patient_id: str):
    """Hastanın tüm vakalarını getir"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patient_cases WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
        cases = cursor.fetchall()
        
        conn.close()
        
        return [{
            "id": c[0], "patient_id": c[1], "case_type": c[2], "clinical_context": c[3],
            "imaging_data": eval(c[4]) if c[4] else None,
            "lab_data": eval(c[5]) if c[5] else None,
            "notes": c[6], "created_at": c[7]
        } for c in cases]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vaka listesi hatası: {str(e)}")


