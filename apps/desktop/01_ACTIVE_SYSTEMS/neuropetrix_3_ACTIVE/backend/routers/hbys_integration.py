from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import json
import logging
from datetime import datetime, timedelta
import asyncio

router = APIRouter(prefix="/hbys", tags=["HBYS Integration"])

class PatientDemographics(BaseModel):
    patient_id: str
    mrn: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class LaboratoryResult(BaseModel):
    test_id: str
    test_name: str
    result_value: str
    unit: str
    reference_range: str
    result_date: str
    status: str  # "normal", "high", "low", "critical"

class ICDDiagnosis(BaseModel):
    icd_code: str
    diagnosis_name: str
    diagnosis_date: str
    severity: str  # "mild", "moderate", "severe"
    status: str  # "active", "resolved", "chronic"

class HBYSRequest(BaseModel):
    patient_id: str
    request_type: str  # "demographics", "lab_results", "diagnoses", "all"
    date_from: Optional[str] = None
    date_to: Optional[str] = None

class HBYSResponse(BaseModel):
    patient_id: str
    demographics: Optional[PatientDemographics] = None
    laboratory_results: Optional[List[LaboratoryResult]] = None
    diagnoses: Optional[List[ICDDiagnosis]] = None
    last_updated: str
    source_system: str

# Mock HBYS FHIR server configuration
HBYS_CONFIG = {
    "base_url": "http://localhost:8080/fhir",  # Mock FHIR server
    "api_key": "mock_api_key_12345",
    "timeout": 30
}

# Mock patient data for demonstration
MOCK_PATIENTS = {
    "P001": {
        "demographics": {
            "patient_id": "P001",
            "mrn": "MRN001234",
            "first_name": "Ahmet",
            "last_name": "Yılmaz",
            "date_of_birth": "1985-03-15",
            "gender": "male",
            "phone": "+90 532 123 4567",
            "email": "ahmet.yilmaz@email.com",
            "address": "Atatürk Cad. No:123, Ankara"
        },
        "laboratory_results": [
            {
                "test_id": "LAB001",
                "test_name": "Glucose",
                "result_value": "95",
                "unit": "mg/dL",
                "reference_range": "70-100",
                "result_date": "2024-08-25",
                "status": "normal"
            },
            {
                "test_id": "LAB002", 
                "test_name": "Creatinine",
                "result_value": "1.2",
                "unit": "mg/dL",
                "reference_range": "0.7-1.3",
                "result_date": "2024-08-25",
                "status": "normal"
            },
            {
                "test_id": "LAB003",
                "test_name": "Hemoglobin",
                "result_value": "13.5",
                "unit": "g/dL", 
                "reference_range": "12-16",
                "result_date": "2024-08-25",
                "status": "normal"
            }
        ],
        "diagnoses": [
            {
                "icd_code": "C34.90",
                "diagnosis_name": "Lung cancer, unspecified",
                "diagnosis_date": "2024-06-15",
                "severity": "moderate",
                "status": "active"
            },
            {
                "icd_code": "E11.9",
                "diagnosis_name": "Type 2 diabetes mellitus without complications",
                "diagnosis_date": "2020-03-10",
                "severity": "mild",
                "status": "chronic"
            }
        ]
    },
    "P002": {
        "demographics": {
            "patient_id": "P002",
            "mrn": "MRN005678",
            "first_name": "Fatma",
            "last_name": "Kaya",
            "date_of_birth": "1978-07-22",
            "gender": "female",
            "phone": "+90 533 987 6543",
            "email": "fatma.kaya@email.com",
            "address": "İnönü Sok. No:45, İstanbul"
        },
        "laboratory_results": [
            {
                "test_id": "LAB004",
                "test_name": "Glucose",
                "result_value": "110",
                "unit": "mg/dL",
                "reference_range": "70-100",
                "result_date": "2024-08-26",
                "status": "high"
            },
            {
                "test_id": "LAB005",
                "test_name": "HbA1c",
                "result_value": "7.2",
                "unit": "%",
                "reference_range": "4.0-5.6",
                "result_date": "2024-08-26",
                "status": "high"
            }
        ],
        "diagnoses": [
            {
                "icd_code": "C50.90",
                "diagnosis_name": "Breast cancer, unspecified",
                "diagnosis_date": "2024-05-20",
                "severity": "moderate",
                "status": "active"
            }
        ]
    }
}

async def fetch_from_hbys_fhir(patient_id: str, resource_type: str) -> Dict[str, Any]:
    """Mock FHIR API call to HBYS system"""
    # Simulate network delay
    await asyncio.sleep(0.5)
    
    if patient_id not in MOCK_PATIENTS:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    
    patient_data = MOCK_PATIENTS[patient_id]
    
    if resource_type == "Patient":
        return patient_data["demographics"]
    elif resource_type == "Observation":
        return {"results": patient_data["laboratory_results"]}
    elif resource_type == "Condition":
        return {"diagnoses": patient_data["diagnoses"]}
    else:
        return patient_data

@router.post("/fetch", response_model=HBYSResponse)
async def fetch_patient_data(request: HBYSRequest):
    """HBYS'den hasta verilerini çek"""
    
    try:
        patient_id = request.patient_id
        
        # Fetch data based on request type
        if request.request_type == "demographics":
            demographics = await fetch_from_hbys_fhir(patient_id, "Patient")
            return HBYSResponse(
                patient_id=patient_id,
                demographics=PatientDemographics(**demographics),
                last_updated=datetime.now().isoformat(),
                source_system="HBYS_FHIR"
            )
            
        elif request.request_type == "lab_results":
            lab_data = await fetch_from_hbys_fhir(patient_id, "Observation")
            lab_results = [LaboratoryResult(**result) for result in lab_data["results"]]
            return HBYSResponse(
                patient_id=patient_id,
                laboratory_results=lab_results,
                last_updated=datetime.now().isoformat(),
                source_system="HBYS_FHIR"
            )
            
        elif request.request_type == "diagnoses":
            diagnosis_data = await fetch_from_hbys_fhir(patient_id, "Condition")
            diagnoses = [ICDDiagnosis(**diag) for diag in diagnosis_data["diagnoses"]]
            return HBYSResponse(
                patient_id=patient_id,
                diagnoses=diagnoses,
                last_updated=datetime.now().isoformat(),
                source_system="HBYS_FHIR"
            )
            
        elif request.request_type == "all":
            # Fetch all data
            demographics = await fetch_from_hbys_fhir(patient_id, "Patient")
            lab_data = await fetch_from_hbys_fhir(patient_id, "Observation")
            diagnosis_data = await fetch_from_hbys_fhir(patient_id, "Condition")
            
            lab_results = [LaboratoryResult(**result) for result in lab_data["results"]]
            diagnoses = [ICDDiagnosis(**diag) for diag in diagnosis_data["diagnoses"]]
            
            return HBYSResponse(
                patient_id=patient_id,
                demographics=PatientDemographics(**demographics),
                laboratory_results=lab_results,
                diagnoses=diagnoses,
                last_updated=datetime.now().isoformat(),
                source_system="HBYS_FHIR"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid request_type")
            
    except Exception as e:
        logging.error(f"HBYS fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HBYS integration error: {str(e)}")

@router.get("/patients")
async def list_available_patients():
    """HBYS'de mevcut hasta listesini getir"""
    patients = []
    for patient_id, data in MOCK_PATIENTS.items():
        patients.append({
            "patient_id": patient_id,
            "mrn": data["demographics"]["mrn"],
            "name": f"{data['demographics']['first_name']} {data['demographics']['last_name']}",
            "date_of_birth": data["demographics"]["date_of_birth"],
            "gender": data["demographics"]["gender"]
        })
    return {"patients": patients}

@router.get("/health")
async def hbys_health_check():
    """HBYS bağlantı durumunu kontrol et"""
    try:
        # Simulate connection test
        await asyncio.sleep(0.2)
        
        return {
            "status": "connected",
            "system": "HBYS_FHIR",
            "last_check": datetime.now().isoformat(),
            "available_patients": len(MOCK_PATIENTS)
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "system": "HBYS_FHIR",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

@router.post("/sync")
async def sync_patient_data(background_tasks: BackgroundTasks, patient_id: str):
    """Hasta verilerini NeuroPETrix'e senkronize et"""
    
    try:
        # Fetch all patient data
        hbys_response = await fetch_patient_data(HBYSRequest(
            patient_id=patient_id,
            request_type="all"
        ))
        
        # TODO: Save to NeuroPETrix database
        # This would integrate with the existing patient management system
        
        return {
            "status": "synced",
            "patient_id": patient_id,
            "synced_data": {
                "demographics": hbys_response.demographics is not None,
                "laboratory_results": len(hbys_response.laboratory_results) if hbys_response.laboratory_results else 0,
                "diagnoses": len(hbys_response.diagnoses) if hbys_response.diagnoses else 0
            },
            "sync_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")

@router.get("/lab-trends/{patient_id}")
async def get_laboratory_trends(patient_id: str, test_name: Optional[str] = None):
    """Laboratuvar sonuçlarının trend analizini getir"""
    
    try:
        lab_data = await fetch_from_hbys_fhir(patient_id, "Observation")
        
        if test_name:
            # Filter by specific test
            filtered_results = [
                result for result in lab_data["results"] 
                if result["test_name"].lower() == test_name.lower()
            ]
        else:
            filtered_results = lab_data["results"]
        
        # Group by test name
        trends = {}
        for result in filtered_results:
            test_name = result["test_name"]
            if test_name not in trends:
                trends[test_name] = []
            
            trends[test_name].append({
                "date": result["result_date"],
                "value": float(result["result_value"]),
                "unit": result["unit"],
                "status": result["status"]
            })
        
        return {
            "patient_id": patient_id,
            "trends": trends,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Lab trends failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trend analysis error: {str(e)}")
