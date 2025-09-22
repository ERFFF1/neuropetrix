from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
from datetime import datetime

router = APIRouter(prefix="/evidence", tags=["Evidence-Based Medicine"])

@router.post("/search")
async def search_evidence(payload: Dict[str, Any]):
    """Literatür arama endpoint'i"""
    try:
        pico_question = payload.get("picoQuestion", {})
        databases = payload.get("databases", ["PubMed", "Cochrane", "Embase"])
        date_range = payload.get("dateRange", {})
        
        # Simüle edilmiş literatür arama sonuçları
        search_results = {
            "searchStrategy": f"({pico_question.get('population', '')}) AND ({pico_question.get('intervention', '')})",
            "databases": databases,
            "inclusionCriteria": [
                "Randomized controlled trials",
                "Systematic reviews",
                "Meta-analyses",
                "Published in last 5 years"
            ],
            "exclusionCriteria": [
                "Case reports",
                "Animal studies",
                "Non-English publications"
            ],
            "results": [
                {
                    "title": "FDG-PET/CT in Lung Cancer Diagnosis: A Meta-Analysis",
                    "authors": "Smith J, et al.",
                    "journal": "Journal of Nuclear Medicine",
                    "year": 2023,
                    "doi": "10.1000/jnm.2023.001",
                    "abstract": "Systematic review of FDG-PET/CT diagnostic accuracy...",
                    "evidence_level": "1A",
                    "relevance_score": 0.95
                },
                {
                    "title": "PET/CT vs CT Alone in Cancer Staging",
                    "authors": "Johnson A, et al.",
                    "journal": "European Journal of Nuclear Medicine",
                    "year": 2022,
                    "doi": "10.1000/ejnm.2022.002",
                    "abstract": "Comparative study of PET/CT vs conventional CT...",
                    "evidence_level": "1B",
                    "relevance_score": 0.87
                }
            ],
            "total_results": 2,
            "search_date": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "evidenceSearch": search_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Literatür arama hatası: {str(e)}")

@router.post("/appraise")
async def appraise_evidence(payload: Dict[str, Any]):
    """Eleştirel değerlendirme endpoint'i"""
    try:
        evidence_search = payload.get("evidenceSearch", {})
        patient_data = payload.get("patientData", {})
        
        # Simüle edilmiş eleştirel değerlendirme
        critical_appraisal = {
            "studyDesign": "Systematic Review and Meta-Analysis",
            "sampleSize": 1250,
            "biasRisk": "low",
            "methodologyQuality": 9,
            "statisticalPower": 8,
            "limitations": [
                "Heterogeneity among included studies",
                "Publication bias possible"
            ],
            "strengths": [
                "Comprehensive literature search",
                "Quality assessment performed",
                "Statistical analysis appropriate"
            ],
            "applicability": {
                "population_match": 0.9,
                "intervention_match": 0.95,
                "outcome_relevance": 0.88
            }
        }
        
        return {
            "success": True,
            "criticalAppraisal": critical_appraisal
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eleştirel değerlendirme hatası: {str(e)}")

@router.post("/applicability")
async def analyze_applicability(payload: Dict[str, Any]):
    """Uygulanabilirlik analizi endpoint'i"""
    try:
        critical_appraisal = payload.get("criticalAppraisal", {})
        patient_data = payload.get("patientData", {})
        comorbidities = payload.get("comorbidities", [])
        medications = payload.get("medications", [])
        
        # Uygulanabilirlik analizi
        applicability_analysis = {
            "patientComorbidities": comorbidities,
            "drugInteractions": [
                "No significant interactions with current medications"
            ],
            "toxicityRisks": [
                "Standard radiation exposure from PET/CT",
                "Contrast allergy risk assessment needed"
            ],
            "contraindications": [
                "Pregnancy (if applicable)",
                "Severe renal impairment"
            ],
            "applicabilityScore": 8.5,
            "recommendation": "strong",
            "reasoning": "High-quality evidence with good applicability to patient population. Benefits outweigh risks.",
            "clinical_decision": {
                "recommended": True,
                "confidence": 0.85,
                "alternative_options": [
                    "Conventional CT staging",
                    "MRI if available"
                ]
            }
        }
        
        return {
            "success": True,
            "applicabilityAnalysis": applicability_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Uygulanabilirlik analizi hatası: {str(e)}")

@router.get("/guidelines/{condition}")
async def get_clinical_guidelines(condition: str):
    """Klinik kılavuzları getirme endpoint'i"""
    try:
        # Simüle edilmiş kılavuz verileri
        guidelines = {
            "lung_cancer": {
                "title": "NCCN Guidelines for Lung Cancer Screening",
                "version": "2024.1",
                "recommendations": [
                    "Annual LDCT screening for high-risk patients",
                    "FDG-PET/CT for suspicious nodules >8mm",
                    "Biopsy confirmation for PET-positive lesions"
                ],
                "evidence_levels": {
                    "screening": "1A",
                    "pet_ct": "1B",
                    "biopsy": "2A"
                }
            },
            "lymphoma": {
                "title": "ESMO Guidelines for Lymphoma Management",
                "version": "2023.2",
                "recommendations": [
                    "FDG-PET/CT for initial staging",
                    "Interim PET for response assessment",
                    "Deauville criteria for interpretation"
                ],
                "evidence_levels": {
                    "staging": "1A",
                    "response_assessment": "1B",
                    "interpretation": "2A"
                }
            }
        }
        
        return {
            "success": True,
            "guidelines": guidelines.get(condition, {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kılavuz getirme hatası: {str(e)}")


