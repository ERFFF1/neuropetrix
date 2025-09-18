from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from datetime import datetime

router = APIRouter(prefix="/clinical-workflow", tags=["Clinical Workflow"])

# Clinical Workflow Configuration
CLINICAL_WORKFLOW = {
    "branches": {
        "oncology": {
            "name": "Onkoloji",
            "icd_codes": ["C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "SUVmax Hesaplama",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "staging": "Evreleme",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip",
                "screening": "Tarama"
            }
        },
        "cardiology": {
            "name": "Kardiyoloji",
            "icd_codes": ["I20", "I21", "I22", "I23", "I24", "I25"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "PET Perfüzyon Analizi",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "prognosis": "Prognoz",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip"
            }
        },
        "neurology": {
            "name": "Nöroloji",
            "icd_codes": ["G30", "G31", "G32", "G93", "G94"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "PET Metabolik Analizi",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "prognosis": "Prognoz",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip"
            }
        },
        "endocrinology": {
            "name": "Endokrinoloji",
            "icd_codes": ["E10", "E11", "E12", "E13", "E14"],
            "workflow_steps": [
                "ICD Kod Girişi",
                "Klinik Hedef Seçimi",
                "Literatür Taraması",
                "PET Metabolik Analizi",
                "Segmentasyon ve Analiz",
                "Klinik Yorumlama",
                "Rapor Üretimi",
                "Takip Planlaması"
            ],
            "clinical_targets": {
                "diagnosis": "Tanı",
                "prognosis": "Prognoz",
                "treatment_response": "Tedaviye Yanıt",
                "follow_up": "Takip"
            }
        }
    }
}

# Pydantic Models
class ICDAnalysisRequest(BaseModel):
    icd_code: str

class ICDAnalysisResponse(BaseModel):
    icd_code: str
    detected_branch: Optional[str]
    branch_name: Optional[str]
    clinical_targets: Optional[Dict[str, str]]
    workflow_steps: Optional[List[str]]

class WorkflowExecutionRequest(BaseModel):
    icd_code: str
    clinical_target: str
    patient_id: Optional[str] = None

class WorkflowExecutionResponse(BaseModel):
    workflow_id: str
    icd_code: str
    branch: str
    clinical_target: str
    steps: List[str]
    status: str
    started_at: str
    completed_at: Optional[str] = None
    results: Optional[Dict] = None

# Endpoints
@router.get("/branches")
async def get_clinical_branches():
    """Tüm klinik branşları ve ICD kodlarını getir"""
    return {
        "status": "success",
        "data": CLINICAL_WORKFLOW["branches"]
    }

@router.post("/analyze-icd", response_model=ICDAnalysisResponse)
async def analyze_icd_code(request: ICDAnalysisRequest):
    """ICD kodunu analiz et ve branş tespit et"""
    icd_code = request.icd_code.upper()
    
    # ICD kodunu analiz et
    detected_branch = None
    for branch_name, branch_data in CLINICAL_WORKFLOW["branches"].items():
        for code in branch_data["icd_codes"]:
            if code in icd_code:
                detected_branch = branch_name
                break
        if detected_branch:
            break
    
    if detected_branch:
        branch_data = CLINICAL_WORKFLOW["branches"][detected_branch]
        return ICDAnalysisResponse(
            icd_code=icd_code,
            detected_branch=detected_branch,
            branch_name=branch_data["name"],
            clinical_targets=branch_data["clinical_targets"],
            workflow_steps=branch_data["workflow_steps"]
        )
    else:
        return ICDAnalysisResponse(
            icd_code=icd_code,
            detected_branch=None,
            branch_name=None,
            clinical_targets=None,
            workflow_steps=None
        )

@router.post("/execute-workflow", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """Klinik workflow'u çalıştır"""
    icd_code = request.icd_code.upper()
    clinical_target = request.clinical_target
    
    # Branş tespit et
    detected_branch = None
    for branch_name, branch_data in CLINICAL_WORKFLOW["branches"].items():
        for code in branch_data["icd_codes"]:
            if code in icd_code:
                detected_branch = branch_name
                break
        if detected_branch:
            break
    
    if not detected_branch:
        raise HTTPException(status_code=400, detail="ICD kodu tanınmadı")
    
    branch_data = CLINICAL_WORKFLOW["branches"][detected_branch]
    
    # Workflow ID oluştur
    workflow_id = f"WF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.patient_id or 'ANON'}"
    
    # Mock workflow execution
    workflow_steps = branch_data["workflow_steps"]
    
    # Simüle edilmiş workflow sonuçları
    mock_results = {
        "literature_search": {
            "found_studies": 15,
            "meta_analyses": 3,
            "grade_evidence": "High"
        },
        "suv_analysis": {
            "baseline_suvmax": 8.5,
            "current_suvmax": 5.2,
            "change_percent": -38.8,
            "percist_response": "Partial Response"
        },
        "segmentation": {
            "lesions_detected": 3,
            "largest_lesion_size": "2.4 cm",
            "segmentation_quality": 95
        },
        "clinical_interpretation": {
            "malignancy_probability": 78,
            "treatment_response": "Good",
            "prognosis": "Moderate",
            "recommended_followup": "3 months"
        }
    }
    
    return WorkflowExecutionResponse(
        workflow_id=workflow_id,
        icd_code=icd_code,
        branch=detected_branch,
        clinical_target=clinical_target,
        steps=workflow_steps,
        status="completed",
        started_at=datetime.now().isoformat(),
        completed_at=datetime.now().isoformat(),
        results=mock_results
    )

@router.get("/workflow-status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Workflow durumunu sorgula"""
    # Mock workflow status
    return {
        "status": "success",
        "data": {
            "workflow_id": workflow_id,
            "status": "completed",
            "progress": 100,
            "current_step": "Takip Planlaması",
            "started_at": datetime.now().isoformat(),
            "estimated_completion": datetime.now().isoformat()
        }
    }

@router.get("/icd-codes")
async def get_all_icd_codes():
    """Tüm desteklenen ICD kodlarını getir"""
    all_codes = []
    for branch_name, branch_data in CLINICAL_WORKFLOW["branches"].items():
        for code in branch_data["icd_codes"]:
            all_codes.append({
                "code": code,
                "branch": branch_name,
                "branch_name": branch_data["name"]
            })
    
    return {
        "status": "success",
        "data": {
            "total_codes": len(all_codes),
            "codes": all_codes
        }
    }

@router.get("/health")
async def health_check():
    """Clinical Workflow API sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "Clinical Workflow API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "supported_branches": list(CLINICAL_WORKFLOW["branches"].keys())
    }

