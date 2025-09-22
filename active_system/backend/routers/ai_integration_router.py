"""
AI Integration Router - JSON Varyasyon + GPT4All + Gemini API'leri
Klinik yorum ve öneri sistemi
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from backend.core.ai_integration import (
    ai_integration_engine, ClinicalContext, ClinicalInterpretation
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-integration", tags=["AI Integration"])

class ClinicalContextRequest(BaseModel):
    """Klinik Bağlam İsteği"""
    body_region: str = Field(..., description="Vücut bölgesi")
    organ: str = Field(..., description="Organ")
    variation_type: str = Field(..., description="Varyasyon tipi (physiological/pathological)")
    suv_max: float = Field(..., description="SUVmax değeri")
    tracer_type: str = Field("FDG", description="Tracer tipi")
    patient_age_group: str = Field(..., description="Hasta yaş grubu")
    clinical_goal: str = Field(..., description="Klinik hedef")
    icd_codes: List[str] = Field(default_factory=list, description="ICD kodları")

class ClinicalInterpretationResponse(BaseModel):
    """Klinik Yorum Yanıtı"""
    success: bool
    interpretation_id: str
    json_variation: str
    gpt4all_comment: str
    gemini_suggestion: str
    final_interpretation: str
    confidence_score: float
    recommendations: List[str]
    message: str

class AIStatusResponse(BaseModel):
    """AI Durum Yanıtı"""
    success: bool
    gpt4all_available: bool
    gemini_available: bool
    clinical_variations_loaded: bool
    variations_count: int
    message: str

@router.get("/health")
async def ai_integration_health():
    """AI Integration servis sağlık kontrolü"""
    ai_status = ai_integration_engine.get_ai_status()
    
    return {
        "status": "healthy",
        "service": "AI Integration Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "ai_status": ai_status
    }

@router.post("/clinical-interpretation", response_model=ClinicalInterpretationResponse)
async def generate_clinical_interpretation(request: ClinicalContextRequest):
    """Klinik yorum oluştur"""
    try:
        logger.info(f"Klinik yorum oluşturuluyor - Bölge: {request.body_region}, Organ: {request.organ}")
        
        # ClinicalContext oluştur
        context = ClinicalContext(
            body_region=request.body_region,
            organ=request.organ,
            variation_type=request.variation_type,
            suv_max=request.suv_max,
            tracer_type=request.tracer_type,
            patient_age_group=request.patient_age_group,
            clinical_goal=request.clinical_goal,
            icd_codes=request.icd_codes
        )
        
        # Klinik yorum oluştur
        interpretation = ai_integration_engine.generate_clinical_interpretation(context)
        
        return ClinicalInterpretationResponse(
            success=True,
            interpretation_id=interpretation.interpretation_id,
            json_variation=interpretation.json_variation,
            gpt4all_comment=interpretation.gpt4all_comment,
            gemini_suggestion=interpretation.gemini_suggestion,
            final_interpretation=interpretation.final_interpretation,
            confidence_score=interpretation.confidence_score,
            recommendations=interpretation.recommendations,
            message="Klinik yorum başarıyla oluşturuldu"
        )
        
    except Exception as e:
        logger.error(f"Klinik yorum oluşturma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Klinik yorum oluşturulamadı: {str(e)}"
        )

@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """AI servislerinin durumunu getir"""
    try:
        ai_status = ai_integration_engine.get_ai_status()
        
        return AIStatusResponse(
            success=True,
            gpt4all_available=ai_status["gpt4all_available"],
            gemini_available=ai_status["gemini_available"],
            clinical_variations_loaded=ai_status["clinical_variations_loaded"],
            variations_count=ai_status["variations_count"],
            message="AI durumu başarıyla alındı"
        )
        
    except Exception as e:
        logger.error(f"AI durumu alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI durumu alınamadı: {str(e)}"
        )

@router.post("/json-variation")
async def get_json_variation(
    body_region: str,
    variation_type: str,
    organ: str,
    suv_max: float
):
    """JSON'dan klinik varyasyon cümlesi al"""
    try:
        logger.info(f"JSON varyasyon alınıyor - Bölge: {body_region}, Organ: {organ}")
        
        # ClinicalContext oluştur
        context = ClinicalContext(
            body_region=body_region,
            organ=organ,
            variation_type=variation_type,
            suv_max=suv_max,
            tracer_type="FDG",
            patient_age_group="19-65",
            clinical_goal="staging",
            icd_codes=[]
        )
        
        # JSON varyasyonu al
        json_variation = ai_integration_engine._get_json_variation(context)
        
        return {
            "success": True,
            "body_region": body_region,
            "variation_type": variation_type,
            "organ": organ,
            "suv_max": suv_max,
            "json_variation": json_variation,
            "message": "JSON varyasyonu başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"JSON varyasyon alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON varyasyonu alınamadı: {str(e)}"
        )

@router.post("/gpt4all-comment")
async def get_gpt4all_comment(request: ClinicalContextRequest):
    """GPT4All ile klinik yorum al"""
    try:
        logger.info(f"GPT4All yorumu alınıyor - Bölge: {request.body_region}")
        
        # ClinicalContext oluştur
        context = ClinicalContext(
            body_region=request.body_region,
            organ=request.organ,
            variation_type=request.variation_type,
            suv_max=request.suv_max,
            tracer_type=request.tracer_type,
            patient_age_group=request.patient_age_group,
            clinical_goal=request.clinical_goal,
            icd_codes=request.icd_codes
        )
        
        # JSON varyasyonu al
        json_variation = ai_integration_engine._get_json_variation(context)
        
        # GPT4All yorumu al
        gpt4all_comment = ai_integration_engine._get_gpt4all_comment(context, json_variation)
        
        return {
            "success": True,
            "json_variation": json_variation,
            "gpt4all_comment": gpt4all_comment,
            "message": "GPT4All yorumu başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"GPT4All yorumu alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GPT4All yorumu alınamadı: {str(e)}"
        )

@router.post("/gemini-suggestion")
async def get_gemini_suggestion(request: ClinicalContextRequest):
    """Gemini ile öneri al"""
    try:
        logger.info(f"Gemini önerisi alınıyor - Bölge: {request.body_region}")
        
        # ClinicalContext oluştur
        context = ClinicalContext(
            body_region=request.body_region,
            organ=request.organ,
            variation_type=request.variation_type,
            suv_max=request.suv_max,
            tracer_type=request.tracer_type,
            patient_age_group=request.patient_age_group,
            clinical_goal=request.clinical_goal,
            icd_codes=request.icd_codes
        )
        
        # JSON varyasyonu al
        json_variation = ai_integration_engine._get_json_variation(context)
        
        # Gemini önerisi al
        gemini_suggestion = ai_integration_engine._get_gemini_suggestion(context, json_variation)
        
        return {
            "success": True,
            "json_variation": json_variation,
            "gemini_suggestion": gemini_suggestion,
            "message": "Gemini önerisi başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Gemini önerisi alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini önerisi alınamadı: {str(e)}"
        )

@router.get("/clinical-variations")
async def get_clinical_variations():
    """Clinical variations verilerini getir"""
    try:
        variations = ai_integration_engine.clinical_variations
        
        return {
            "success": True,
            "clinical_variations": variations,
            "message": "Clinical variations başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Clinical variations alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical variations alınamadı: {str(e)}"
        )

@router.get("/body-regions")
async def get_available_body_regions():
    """Mevcut vücut bölgelerini getir"""
    try:
        variations = ai_integration_engine.clinical_variations
        body_regions = list(variations.get("clinical_variations", {}).keys())
        
        return {
            "success": True,
            "body_regions": body_regions,
            "count": len(body_regions),
            "message": "Vücut bölgeleri başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Vücut bölgeleri alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vücut bölgeleri alınamadı: {str(e)}"
        )

@router.get("/organs/{body_region}")
async def get_organs_for_region(body_region: str):
    """Belirli vücut bölgesi için organları getir"""
    try:
        variations = ai_integration_engine.clinical_variations
        region_variations = variations.get("clinical_variations", {}).get(body_region.lower(), {})
        
        organs = set()
        for variation_type in region_variations.values():
            if isinstance(variation_type, dict):
                organs.update(variation_type.keys())
        
        return {
            "success": True,
            "body_region": body_region,
            "organs": list(organs),
            "count": len(organs),
            "message": f"{body_region} bölgesi organları başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Organlar alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Organlar alınamadı: {str(e)}"
        )

@router.get("/tracer-types")
async def get_available_tracer_types():
    """Mevcut tracer türlerini getir"""
    try:
        tracer_types = [
            {
                "type": "FDG",
                "name": "Fluorodeoxyglucose",
                "description": "Genel metabolik aktivite"
            },
            {
                "type": "PSMA",
                "name": "Prostate-specific membrane antigen",
                "description": "Prostat kanseri"
            },
            {
                "type": "DOTATATE",
                "name": "Somatostatin receptor",
                "description": "Nöroendokrin tümörler"
            },
            {
                "type": "FAPI",
                "name": "Fibroblast activation protein inhibitor",
                "description": "Fibrozis ve tümörler"
            }
        ]
        
        return {
            "success": True,
            "tracer_types": tracer_types,
            "count": len(tracer_types),
            "message": "Tracer türleri başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Tracer türleri alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tracer türleri alınamadı: {str(e)}"
        )

@router.get("/test")
async def test_ai_integration():
    """AI entegrasyonunu test et"""
    try:
        test_result = ai_integration_engine.test_ai_integration()
        
        return {
            "success": test_result["success"],
            "test_result": test_result,
            "message": "AI entegrasyon testi tamamlandı"
        }
        
    except Exception as e:
        logger.error(f"AI entegrasyon test hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI entegrasyon testi başarısız: {str(e)}"
        )

@router.post("/batch-interpretation")
async def batch_clinical_interpretation(requests: List[ClinicalContextRequest]):
    """Toplu klinik yorum oluştur"""
    try:
        logger.info(f"Toplu klinik yorum oluşturuluyor - {len(requests)} istek")
        
        results = []
        
        for i, request in enumerate(requests):
            try:
                # ClinicalContext oluştur
                context = ClinicalContext(
                    body_region=request.body_region,
                    organ=request.organ,
                    variation_type=request.variation_type,
                    suv_max=request.suv_max,
                    tracer_type=request.tracer_type,
                    patient_age_group=request.patient_age_group,
                    clinical_goal=request.clinical_goal,
                    icd_codes=request.icd_codes
                )
                
                # Klinik yorum oluştur
                interpretation = ai_integration_engine.generate_clinical_interpretation(context)
                
                results.append({
                    "index": i,
                    "success": True,
                    "interpretation_id": interpretation.interpretation_id,
                    "final_interpretation": interpretation.final_interpretation,
                    "confidence_score": interpretation.confidence_score
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "total_requests": len(requests),
            "successful_interpretations": success_count,
            "failed_interpretations": len(requests) - success_count,
            "results": results,
            "message": f"{success_count}/{len(requests)} klinik yorum başarıyla oluşturuldu"
        }
        
    except Exception as e:
        logger.error(f"Toplu klinik yorum hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Toplu klinik yorum oluşturulamadı: {str(e)}"
        )
