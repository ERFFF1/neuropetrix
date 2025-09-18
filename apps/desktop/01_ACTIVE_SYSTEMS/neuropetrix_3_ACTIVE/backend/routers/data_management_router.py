"""
Data Management Router - Anonimleştirme & FHIR API'leri
Nash ID eşleştirme, SUV trend logları, FHIR DiagnosticReport
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel, Field
from backend.core.data_manager import (
    data_manager, PatientData, AnonymizedPatient, SUVTrendLog, FHIRDiagnosticReport
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["Data Management"])

class PatientDataRequest(BaseModel):
    """Hasta Verisi İsteği"""
    patient_id: str = Field(..., description="Hasta ID")
    name: str = Field(..., description="Ad")
    surname: str = Field(..., description="Soyad")
    birth_date: str = Field(..., description="Doğum tarihi (YYYY-MM-DD)")
    gender: str = Field(..., description="Cinsiyet")
    mrn: str = Field(..., description="Medical Record Number")
    study_date: str = Field(..., description="Çalışma tarihi")
    study_type: str = Field("PET/CT", description="Çalışma tipi")

class AnonymizeResponse(BaseModel):
    """Anonimleştirme Yanıtı"""
    success: bool
    nash_id: str
    anonymized_patient: Dict[str, Any]
    message: str

class SUVTrendRequest(BaseModel):
    """SUV Trend İsteği"""
    nash_id: str = Field(..., description="Nash ID")
    measurement_date: str = Field(..., description="Ölçüm tarihi")
    suv_max: float = Field(..., description="SUVmax değeri")
    suv_peak: float = Field(..., description="SUVpeak değeri")
    suv_mean: float = Field(..., description="SUVmean değeri")
    location: str = Field(..., description="Ölçüm lokasyonu")
    tracer_type: str = Field("FDG", description="Tracer tipi")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Güven skoru")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Ek veriler")

class FHIRReportRequest(BaseModel):
    """FHIR Rapor İsteği"""
    nash_id: str = Field(..., description="Nash ID")
    findings: List[str] = Field(..., description="Bulgular")
    conclusion: str = Field(..., description="Sonuç")
    study_date: str = Field(..., description="Çalışma tarihi")

@router.get("/health")
async def data_management_health():
    """Data Management servis sağlık kontrolü"""
    summary = data_manager.get_data_summary()
    
    return {
        "status": "healthy",
        "service": "Data Management",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "data_summary": summary
    }

@router.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_patient_data(request: PatientDataRequest):
    """Hasta verisini anonimleştir"""
    try:
        logger.info(f"Hasta verisi anonimleştiriliyor: {request.patient_id}")
        
        # PatientData oluştur
        patient_data = PatientData(
            patient_id=request.patient_id,
            name=request.name,
            surname=request.surname,
            birth_date=request.birth_date,
            gender=request.gender,
            mrn=request.mrn,
            study_date=datetime.fromisoformat(request.study_date),
            study_type=request.study_type
        )
        
        # Anonimleştir
        anonymized_patient = data_manager.anonymize_patient_data(patient_data)
        
        return AnonymizeResponse(
            success=True,
            nash_id=anonymized_patient.nash_id,
            anonymized_patient={
                "nash_id": anonymized_patient.nash_id,
                "age_group": anonymized_patient.age_group,
                "gender": anonymized_patient.gender,
                "study_date": anonymized_patient.study_date.isoformat(),
                "study_type": anonymized_patient.study_type,
                "anonymized_data": anonymized_patient.anonymized_data
            },
            message="Hasta verisi başarıyla anonimleştirildi"
        )
        
    except Exception as e:
        logger.error(f"Anonimleştirme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anonimleştirme başarısız: {str(e)}"
        )

@router.post("/load-old-report")
async def load_old_report(report_data: Dict[str, Any]):
    """Eski raporu yükle ve otomatik anonimleştir"""
    try:
        logger.info("Eski rapor yükleniyor ve anonimleştiriliyor")
        
        # Raporu yükle ve anonimleştir
        anonymized_patient, anonymized_report = data_manager.load_old_report(report_data)
        
        return {
            "success": True,
            "nash_id": anonymized_patient.nash_id,
            "anonymized_patient": {
                "nash_id": anonymized_patient.nash_id,
                "age_group": anonymized_patient.age_group,
                "gender": anonymized_patient.gender,
                "study_date": anonymized_patient.study_date.isoformat(),
                "study_type": anonymized_patient.study_type
            },
            "anonymized_report": anonymized_report,
            "message": "Eski rapor başarıyla yüklendi ve anonimleştirildi"
        }
        
    except Exception as e:
        logger.error(f"Eski rapor yükleme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eski rapor yüklenemedi: {str(e)}"
        )

@router.post("/suv-trend")
async def add_suv_trend_log(request: SUVTrendRequest):
    """SUV trend log ekle"""
    try:
        logger.info(f"SUV trend log ekleniyor - Nash ID: {request.nash_id}")
        
        # SUV verisi oluştur
        suv_data = {
            "measurement_date": request.measurement_date,
            "suv_max": request.suv_max,
            "suv_peak": request.suv_peak,
            "suv_mean": request.suv_mean,
            "location": request.location,
            "tracer_type": request.tracer_type,
            "confidence": request.confidence,
            "metadata": request.metadata or {}
        }
        
        # SUV trend log ekle
        suv_log = data_manager.add_suv_trend_log(request.nash_id, suv_data)
        
        return {
            "success": True,
            "log_id": suv_log.log_id,
            "nash_id": request.nash_id,
            "message": "SUV trend log başarıyla eklendi"
        }
        
    except Exception as e:
        logger.error(f"SUV trend log ekleme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SUV trend log eklenemedi: {str(e)}"
        )

@router.get("/suv-trend/{nash_id}")
async def get_suv_trend_data(nash_id: str):
    """SUV trend verilerini getir"""
    try:
        trend_data = data_manager.get_suv_trend_data(nash_id)
        
        return {
            "success": True,
            "nash_id": nash_id,
            "trend_data": trend_data,
            "message": "SUV trend verileri başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"SUV trend verileri alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SUV trend verileri alınamadı: {str(e)}"
        )

@router.post("/fhir-report")
async def create_fhir_diagnostic_report(request: FHIRReportRequest):
    """FHIR DiagnosticReport oluştur"""
    try:
        logger.info(f"FHIR DiagnosticReport oluşturuluyor - Nash ID: {request.nash_id}")
        
        # Rapor verisi oluştur
        report_data = {
            "findings": request.findings,
            "conclusion": request.conclusion,
            "study_date": request.study_date
        }
        
        # FHIR raporu oluştur
        fhir_report = data_manager.create_fhir_diagnostic_report(request.nash_id, report_data)
        
        return {
            "success": True,
            "resource_id": fhir_report.resource_id,
            "nash_id": request.nash_id,
            "fhir_report": fhir_report.fhir_data,
            "message": "FHIR DiagnosticReport başarıyla oluşturuldu"
        }
        
    except Exception as e:
        logger.error(f"FHIR raporu oluşturma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR raporu oluşturulamadı: {str(e)}"
        )

@router.get("/fhir-report/{resource_id}")
async def get_fhir_report(resource_id: str):
    """FHIR raporu getir"""
    try:
        fhir_report = data_manager.get_fhir_report(resource_id)
        
        if not fhir_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FHIR raporu bulunamadı"
            )
        
        return {
            "success": True,
            "resource_id": resource_id,
            "fhir_report": fhir_report,
            "message": "FHIR raporu başarıyla alındı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"FHIR raporu alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR raporu alınamadı: {str(e)}"
        )

@router.get("/fhir-reports/{nash_id}")
async def get_patient_fhir_reports(nash_id: str):
    """Hastanın FHIR raporlarını getir"""
    try:
        fhir_reports = data_manager.get_patient_fhir_reports(nash_id)
        
        return {
            "success": True,
            "nash_id": nash_id,
            "fhir_reports": fhir_reports,
            "count": len(fhir_reports),
            "message": f"{len(fhir_reports)} FHIR raporu bulundu"
        }
        
    except Exception as e:
        logger.error(f"Hasta FHIR raporları alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hasta FHIR raporları alınamadı: {str(e)}"
        )

@router.get("/fhir-bundle/{nash_id}")
async def export_fhir_bundle(nash_id: str):
    """FHIR Bundle oluştur (hasta için tüm veriler)"""
    try:
        fhir_bundle = data_manager.export_fhir_bundle(nash_id)
        
        if "error" in fhir_bundle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=fhir_bundle["error"]
            )
        
        return {
            "success": True,
            "nash_id": nash_id,
            "fhir_bundle": fhir_bundle,
            "message": "FHIR Bundle başarıyla oluşturuldu"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"FHIR Bundle oluşturma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR Bundle oluşturulamadı: {str(e)}"
        )

@router.get("/nash-id/{mrn}")
async def get_nash_id_from_mrn(mrn: str):
    """MRN'den Nash ID al"""
    try:
        nash_id = data_manager.get_nash_id_from_mrn(mrn)
        
        if not nash_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MRN için Nash ID bulunamadı"
            )
        
        return {
            "success": True,
            "mrn": mrn,
            "nash_id": nash_id,
            "message": "Nash ID başarıyla alındı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nash ID alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nash ID alınamadı: {str(e)}"
        )

@router.get("/patient/{nash_id}")
async def get_anonymized_patient(nash_id: str):
    """Anonimleştirilmiş hasta verisini getir"""
    try:
        patient = data_manager.get_anonymized_patient(nash_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anonimleştirilmiş hasta bulunamadı"
            )
        
        return {
            "success": True,
            "nash_id": nash_id,
            "patient": {
                "nash_id": patient.nash_id,
                "age_group": patient.age_group,
                "gender": patient.gender,
                "study_date": patient.study_date.isoformat(),
                "study_type": patient.study_type,
                "anonymized_data": patient.anonymized_data
            },
            "message": "Anonimleştirilmiş hasta verisi başarıyla alındı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anonimleştirilmiş hasta verisi alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anonimleştirilmiş hasta verisi alınamadı: {str(e)}"
        )

@router.get("/summary")
async def get_data_summary():
    """Veri özeti getir"""
    try:
        summary = data_manager.get_data_summary()
        
        return {
            "success": True,
            "data_summary": summary,
            "message": "Veri özeti başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Veri özeti alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Veri özeti alınamadı: {str(e)}"
        )

# Test endpoint
@router.get("/test")
async def test_data_manager():
    """Data Manager test"""
    try:
        # Test hasta verisi
        patient_data = PatientData(
            patient_id="TEST_001",
            name="Test",
            surname="Patient",
            birth_date="1980-01-01",
            gender="male",
            mrn="TEST_MRN_001",
            study_date=datetime.now(),
            study_type="FDG-PET/CT"
        )
        
        # Anonimleştir
        anonymized = data_manager.anonymize_patient_data(patient_data)
        
        # SUV trend log ekle
        suv_data = {
            "measurement_date": datetime.now().isoformat(),
            "suv_max": 4.5,
            "suv_peak": 4.2,
            "suv_mean": 3.8,
            "location": "Primer tümör",
            "tracer_type": "FDG",
            "confidence": 0.9
        }
        
        suv_log = data_manager.add_suv_trend_log(anonymized.nash_id, suv_data)
        
        # FHIR raporu oluştur
        report_data = {
            "findings": ["Primer tümör tespit edildi"],
            "conclusion": "Malign lezyon",
            "study_date": datetime.now().isoformat()
        }
        
        fhir_report = data_manager.create_fhir_diagnostic_report(anonymized.nash_id, report_data)
        
        return {
            "success": True,
            "test_results": {
                "nash_id": anonymized.nash_id,
                "suv_log_id": suv_log.log_id,
                "fhir_report_id": fhir_report.resource_id
            },
            "message": "Data Manager test başarılı"
        }
        
    except Exception as e:
        logger.error(f"Data Manager test hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data Manager test başarısız: {str(e)}"
        )
