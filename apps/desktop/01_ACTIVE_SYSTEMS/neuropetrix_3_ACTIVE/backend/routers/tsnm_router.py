"""
TSNM Raporlama Router
PERCIST standardına uygun raporlama API'leri
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from backend.core.tsnm_engine import (
    TSNMEngine, TSNMFindings, SUVMeasurement, 
    TSNMStage, TracerType, PERCISTResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tsnm", tags=["TSNM Reporting"])

# TSNM Engine instance
tsnm_engine = TSNMEngine()

class SUVMeasurementRequest(BaseModel):
    """SUV Ölçüm İsteği"""
    value: float = Field(..., description="SUV değeri")
    location: str = Field(..., description="Ölçüm lokasyonu")
    measurement_type: str = Field(..., description="Ölçüm tipi (peak, max, mean)")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Güven skoru")

class TSNMFindingsRequest(BaseModel):
    """TSNM Bulgular İsteği"""
    primary_tumor: Optional[str] = Field(None, description="Primer tümör evresi (T0-T4)")
    lymph_nodes: Optional[str] = Field(None, description="Lenf nodu evresi (N0-N2)")
    metastasis: Optional[str] = Field(None, description="Metastaz evresi (M0-M1)")
    tracer_type: str = Field("FDG", description="PET tracer tipi")
    suv_measurements: List[SUVMeasurementRequest] = Field(default_factory=list)
    clinical_goal: str = Field("staging", description="Klinik hedef")
    icd_codes: List[str] = Field(default_factory=list, description="ICD-10 kodları")

class TSNMAnalysisResponse(BaseModel):
    """TSNM Analiz Yanıtı"""
    success: bool
    analysis: Dict[str, Any]
    report: str
    timestamp: datetime
    message: str

class PERCISTAnalysisRequest(BaseModel):
    """PERCIST Analiz İsteği"""
    baseline_suv: float = Field(..., description="Baseline SUV değeri")
    followup_suv: float = Field(..., description="Follow-up SUV değeri")
    tracer_type: str = Field("FDG", description="PET tracer tipi")
    measurement_location: str = Field(..., description="Ölçüm lokasyonu")

class PERCISTAnalysisResponse(BaseModel):
    """PERCIST Analiz Yanıtı"""
    success: bool
    baseline_suv: float
    followup_suv: float
    delta_suv_percent: float
    response: str
    confidence: float
    threshold_used: float
    interpretation: str
    recommendations: List[str]

@router.get("/health")
async def tsnm_health():
    """TSNM servis sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "TSNM Reporting Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/analyze", response_model=TSNMAnalysisResponse)
async def analyze_tsnm(findings_request: TSNMFindingsRequest):
    """TSNM analizi yap"""
    try:
        logger.info(f"TSNM analizi başlatıldı - Tracer: {findings_request.tracer_type}")
        
        # Request'i TSNMFindings'a dönüştür
        findings = _convert_to_tsnm_findings(findings_request)
        
        # TSNM analizi yap
        analysis = tsnm_engine.analyze_tsnm(findings)
        
        # Rapor oluştur
        report = tsnm_engine.generate_report(analysis)
        
        return TSNMAnalysisResponse(
            success=True,
            analysis=analysis,
            report=report,
            timestamp=datetime.now(),
            message="TSNM analizi başarıyla tamamlandı"
        )
        
    except Exception as e:
        logger.error(f"TSNM analiz hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TSNM analizi başarısız: {str(e)}"
        )

@router.post("/percist", response_model=PERCISTAnalysisResponse)
async def analyze_percist(percist_request: PERCISTAnalysisRequest):
    """PERCIST analizi yap"""
    try:
        logger.info(f"PERCIST analizi başlatıldı - Tracer: {percist_request.tracer_type}")
        
        # Tracer tipini belirle
        tracer_type = TracerType(percist_request.tracer_type.upper())
        
        # ΔSUV hesapla
        delta_suv_percent = ((percist_request.followup_suv - percist_request.baseline_suv) / 
                           percist_request.baseline_suv) * 100
        
        # Threshold belirle
        tracer_rules = tsnm_engine.tracer_rules[tracer_type]
        threshold = tracer_rules["delta_threshold"]
        
        # PERCIST yanıt belirleme
        if delta_suv_percent <= -threshold:
            response = PERCISTResponse.PR
        elif delta_suv_percent >= threshold:
            response = PERCISTResponse.PD
        else:
            response = PERCISTResponse.SD
        
        # Güven skoru hesapla
        confidence = tsnm_engine._calculate_confidence(
            percist_request.baseline_suv, 
            percist_request.followup_suv
        )
        
        # Yorum oluştur
        interpretation = _generate_percist_interpretation(
            response, delta_suv_percent, threshold, tracer_type
        )
        
        # Öneriler oluştur
        recommendations = _generate_percist_recommendations(response, tracer_type)
        
        return PERCISTAnalysisResponse(
            success=True,
            baseline_suv=percist_request.baseline_suv,
            followup_suv=percist_request.followup_suv,
            delta_suv_percent=delta_suv_percent,
            response=response.value,
            confidence=confidence,
            threshold_used=threshold,
            interpretation=interpretation,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"PERCIST analiz hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PERCIST analizi başarısız: {str(e)}"
        )

@router.get("/tracers")
async def get_available_tracers():
    """Mevcut tracer türlerini listele"""
    return {
        "tracers": [
            {
                "type": tracer.value,
                "name": _get_tracer_name(tracer),
                "description": _get_tracer_description(tracer),
                "rules": tsnm_engine.tracer_rules[tracer]
            }
            for tracer in TracerType
        ]
    }

@router.get("/templates/{tracer_type}")
async def get_tracer_templates(tracer_type: str):
    """Tracer-specific şablonları getir"""
    try:
        tracer = TracerType(tracer_type.upper())
        templates = tsnm_engine.tsnm_templates.get(tracer.value.lower(), {})
        
        return {
            "tracer_type": tracer.value,
            "templates": templates
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz tracer tipi: {tracer_type}"
        )

@router.get("/variations/{body_region}")
async def get_clinical_variations(body_region: str):
    """Klinik varyasyon cümlelerini getir"""
    try:
        # Clinical variations JSON'ını yükle
        import json
        from pathlib import Path
        
        variations_file = Path(__file__).parent.parent / "core" / "clinical_variations.json"
        
        if not variations_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinical variations dosyası bulunamadı"
            )
        
        with open(variations_file, 'r', encoding='utf-8') as f:
            variations_data = json.load(f)
        
        region_variations = variations_data["clinical_variations"].get(body_region.lower())
        
        if not region_variations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vücut bölgesi bulunamadı: {body_region}"
            )
        
        return {
            "body_region": body_region,
            "variations": region_variations
        }
        
    except Exception as e:
        logger.error(f"Clinical variations hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical variations alınamadı: {str(e)}"
        )

@router.post("/generate-sentence")
async def generate_clinical_sentence(
    body_region: str,
    variation_type: str,  # "physiological" or "pathological"
    organ: str,
    suv_max: Optional[float] = None
):
    """Klinik cümle oluştur"""
    try:
        # Clinical variations JSON'ını yükle
        import json
        from pathlib import Path
        import random
        
        variations_file = Path(__file__).parent.parent / "core" / "clinical_variations.json"
        
        with open(variations_file, 'r', encoding='utf-8') as f:
            variations_data = json.load(f)
        
        region_variations = variations_data["clinical_variations"].get(body_region.lower())
        
        if not region_variations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vücut bölgesi bulunamadı: {body_region}"
            )
        
        organ_variations = region_variations.get(variation_type, {}).get(organ)
        
        if not organ_variations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organ varyasyonu bulunamadı: {organ}"
            )
        
        # Rastgele cümle seç
        sentence_template = random.choice(organ_variations)
        
        # SUVmax değerini ekle
        if suv_max is not None:
            sentence = sentence_template.format(suv_max=suv_max)
        else:
            sentence = sentence_template
        
        return {
            "body_region": body_region,
            "variation_type": variation_type,
            "organ": organ,
            "suv_max": suv_max,
            "sentence": sentence,
            "template": sentence_template
        }
        
    except Exception as e:
        logger.error(f"Clinical sentence generation hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical sentence oluşturulamadı: {str(e)}"
        )

# Helper functions
def _convert_to_tsnm_findings(request: TSNMFindingsRequest) -> TSNMFindings:
    """Request'i TSNMFindings'a dönüştür"""
    # TSNM evrelerini dönüştür
    primary_tumor = TSNMStage(request.primary_tumor) if request.primary_tumor else None
    lymph_nodes = TSNMStage(request.lymph_nodes) if request.lymph_nodes else None
    metastasis = TSNMStage(request.metastasis) if request.metastasis else None
    
    # Tracer tipini dönüştür
    tracer_type = TracerType(request.tracer_type.upper())
    
    # SUV ölçümlerini dönüştür
    suv_measurements = [
        SUVMeasurement(
            value=measurement.value,
            location=measurement.location,
            measurement_type=measurement.measurement_type,
            timestamp=datetime.now(),
            confidence=measurement.confidence
        )
        for measurement in request.suv_measurements
    ]
    
    return TSNMFindings(
        primary_tumor=primary_tumor,
        lymph_nodes=lymph_nodes,
        metastasis=metastasis,
        tracer_type=tracer_type,
        suv_measurements=suv_measurements
    )

def _generate_percist_interpretation(
    response: PERCISTResponse, 
    delta_suv_percent: float, 
    threshold: float,
    tracer_type: TracerType
) -> str:
    """PERCIST yorumu oluştur"""
    tracer_name = _get_tracer_name(tracer_type)
    
    if response == PERCISTResponse.PR:
        return f"{tracer_name}-PET/CT incelemesinde tedaviye kısmi yanıt tespit edilmiştir (ΔSUV: {delta_suv_percent:.1f}%, threshold: {threshold}%)."
    elif response == PERCISTResponse.PD:
        return f"{tracer_name}-PET/CT incelemesinde hastalık progresyonu tespit edilmiştir (ΔSUV: {delta_suv_percent:.1f}%, threshold: {threshold}%)."
    else:
        return f"{tracer_name}-PET/CT incelemesinde stabil hastalık tespit edilmiştir (ΔSUV: {delta_suv_percent:.1f}%, threshold: {threshold}%)."

def _generate_percist_recommendations(response: PERCISTResponse, tracer_type: TracerType) -> List[str]:
    """PERCIST önerileri oluştur"""
    recommendations = []
    
    if response == PERCISTResponse.PR:
        recommendations.append("Tedavi yanıtı mevcut - mevcut tedaviye devam önerilir")
        recommendations.append("3-6 ay sonra kontrol PET/CT önerilir")
    elif response == PERCISTResponse.PD:
        recommendations.append("Hastalık progresyonu - tedavi değişikliği önerilir")
        recommendations.append("Alternatif tedavi seçenekleri değerlendirilmelidir")
    else:
        recommendations.append("Stabil hastalık - mevcut tedaviye devam önerilir")
        recommendations.append("6 ay sonra kontrol PET/CT önerilir")
    
    return recommendations

def _get_tracer_name(tracer: TracerType) -> str:
    """Tracer ismini getir"""
    names = {
        TracerType.FDG: "FDG",
        TracerType.PSMA: "PSMA",
        TracerType.DOTATATE: "DOTATATE",
        TracerType.FAPI: "FAPI"
    }
    return names.get(tracer, tracer.value)

def _get_tracer_description(tracer: TracerType) -> str:
    """Tracer açıklamasını getir"""
    descriptions = {
        TracerType.FDG: "Fluorodeoxyglucose - Genel metabolik aktivite",
        TracerType.PSMA: "Prostate-specific membrane antigen - Prostat kanseri",
        TracerType.DOTATATE: "Somatostatin receptor - Nöroendokrin tümörler",
        TracerType.FAPI: "Fibroblast activation protein inhibitor - Fibrozis ve tümörler"
    }
    return descriptions.get(tracer, "Bilinmeyen tracer")

# Test endpoint
@router.get("/test")
async def test_tsnm_engine():
    """TSNM engine test"""
    try:
        # Test verisi
        findings = TSNMFindings(
            primary_tumor=TSNMStage.T2,
            lymph_nodes=TSNMStage.N1,
            metastasis=TSNMStage.M0,
            tracer_type=TracerType.FDG,
            suv_measurements=[
                SUVMeasurement(4.5, "Primer tümör", "max", datetime.now()),
                SUVMeasurement(3.2, "Lenf nodu", "max", datetime.now())
            ]
        )
        
        # Analiz yap
        analysis = tsnm_engine.analyze_tsnm(findings)
        
        return {
            "success": True,
            "test_analysis": analysis,
            "message": "TSNM engine test başarılı"
        }
        
    except Exception as e:
        logger.error(f"TSNM engine test hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TSNM engine test başarısız: {str(e)}"
        )
