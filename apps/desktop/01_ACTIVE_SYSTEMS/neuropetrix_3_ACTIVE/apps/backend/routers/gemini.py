from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gemini", tags=["gemini"])

# Pydantic modelleri
class AIConclusionRequest(BaseModel):
    clinical_goal: str
    imaging_available: bool
    imaging_metrics: Optional[Dict[str, Any]] = None
    qc_flags: Optional[List[str]] = None
    evidence_summary: Optional[str] = None

class ImagingPipelineRequest(BaseModel):
    dicom_dir: str
    case_meta: Dict[str, Any]

class EvidenceSearchRequest(BaseModel):
    pico: Dict[str, str]
    max_refs: int = 10
    icd10: str
    clinical_goal: str

class FHIRReportRequest(BaseModel):
    diagnostic_report: Dict[str, Any]
    observations: List[Dict[str, Any]]
    annex_document: Optional[Dict[str, Any]] = None

@router.get("/")
async def gemini_root():
    """Gemini AI Studio ana endpoint"""
    return {
        "message": "NeuroPETRIX v2.0 - Gemini AI Studio Integration",
        "version": "1.0.0",
        "status": "active"
    }

@router.get("/info")
async def get_gemini_info():
    """Gemini servis bilgilerini getir"""
    try:
        info = gemini_service.get_system_info()
        return {
            "status": "success",
            "data": info
        }
    except Exception as e:
        logger.error(f"Gemini info error: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini info error: {str(e)}")

@router.post("/generate-conclusion")
async def generate_ai_conclusion(request: AIConclusionRequest):
    """AI sonucu üret"""
    try:
        logger.info(f"Generating AI conclusion for: {request.clinical_goal}")
        
        result = gemini_service.generate_ai_conclusion(
            clinical_goal=request.clinical_goal,
            imaging_available=request.imaging_available,
            imaging_metrics=request.imaging_metrics,
            qc_flags=request.qc_flags,
            evidence_summary=request.evidence_summary
        )
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"AI conclusion generation error: {e}")
        raise HTTPException(status_code=500, detail=f"AI conclusion error: {str(e)}")

@router.post("/imaging-pipeline")
async def run_imaging_pipeline(request: ImagingPipelineRequest):
    """Imaging pipeline çalıştır (mock)"""
    try:
        logger.info(f"Running imaging pipeline for: {request.case_meta.get('patient_id')}")
        
        # Mock implementation - gerçek entegrasyonda Gemini API çağrısı yapılır
        mock_result = {
            "case_id": f"CASE_{request.case_meta.get('patient_id')}",
            "status": "completed",
            "processing_time": 45.2,
            "results": {
                "segmentation": "completed",
                "radiomics": "completed",
                "percist": "PMR" if request.case_meta.get("clinical_goal") == "response" else None,
                "deauville": 2 if request.case_meta.get("clinical_goal") == "lymphoma_followup" else None,
                "suv_metrics": {
                    "suvmax": 8.5,
                    "mtv": 12.3,
                    "tlg": 104.6
                }
            }
        }
        
        return {
            "status": "success",
            "data": mock_result
        }
        
    except Exception as e:
        logger.error(f"Imaging pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Imaging pipeline error: {str(e)}")

@router.post("/evidence-search")
async def search_evidence(request: EvidenceSearchRequest):
    """Kanıt arama (mock)"""
    try:
        logger.info(f"Searching evidence for: {request.icd10}")
        
        # Mock implementation
        mock_results = [
            {
                "title": "Evidence-based guidelines for PET/CT in oncology",
                "authors": "Smith J, et al.",
                "journal": "Journal of Nuclear Medicine",
                "year": 2023,
                "abstract": "Comprehensive review of PET/CT applications in oncology...",
                "grade_score": "GRADE A",
                "relevance_score": 0.95
            },
            {
                "title": "PERCIST criteria validation study",
                "authors": "Johnson M, et al.",
                "journal": "European Journal of Nuclear Medicine",
                "year": 2022,
                "abstract": "Validation of PERCIST criteria in multicenter study...",
                "grade_score": "GRADE B",
                "relevance_score": 0.87
            }
        ]
        
        mock_summary = "Strong evidence (GRADE A) supports PET/CT use in oncology staging and response assessment."
        
        mock_recommendations = [
            "Use PET/CT for initial staging in suspected malignancies",
            "Apply PERCIST criteria for treatment response assessment",
            "Consider Deauville scoring for lymphoma follow-up"
        ]
        
        return {
            "status": "success",
            "data": {
                "search_results": mock_results,
                "grade_summary": mock_summary,
                "clinical_recommendations": mock_recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Evidence search error: {e}")
        raise HTTPException(status_code=500, detail=f"Evidence search error: {str(e)}")

@router.post("/push-fhir")
async def push_fhir_report(request: FHIRReportRequest):
    """FHIR raporu gönder (mock)"""
    try:
        logger.info(f"Pushing FHIR report for: {request.diagnostic_report.get('patient_id')}")
        
        # Mock implementation
        mock_result = {
            "fhir_status": "success",
            "message": "Report successfully sent to HBYS",
            "report_id": f"FHIR_{request.diagnostic_report.get('patient_id')}",
            "timestamp": "2024-12-19T22:35:00Z"
        }
        
        return {
            "status": "success",
            "data": mock_result
        }
        
    except Exception as e:
        logger.error(f"FHIR push error: {e}")
        raise HTTPException(status_code=500, detail=f"FHIR push error: {str(e)}")

@router.get("/validate-schema")
async def validate_output_schema():
    """Output schema validation"""
    try:
        schema = gemini_service.output_schema
        validation_rules = schema.get("validation_rules", {})
        
        return {
            "status": "success",
            "data": {
                "schema_loaded": bool(schema),
                "validation_rules": validation_rules,
                "example_outputs": schema.get("example_outputs", {})
            }
        }
        
    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Schema validation error: {str(e)}")

@router.get("/tools")
async def get_available_tools():
    """Kullanılabilir araçları listele"""
    try:
        tools = gemini_service.tools_config.get("tools", [])
        
        return {
            "status": "success",
            "data": {
                "tools_count": len(tools),
                "tools": [{"name": tool["name"], "description": tool["description"]} for tool in tools]
            }
        }
        
    except Exception as e:
        logger.error(f"Tools listing error: {e}")
        raise HTTPException(status_code=500, detail=f"Tools listing error: {str(e)}")


