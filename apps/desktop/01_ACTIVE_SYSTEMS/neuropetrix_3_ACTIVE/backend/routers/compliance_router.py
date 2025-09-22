"""
Compliance Router - CE-MDR/ISO 13485 & Patentli Modül API'leri
Compliance Reporter ve IP koruması
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from backend.core.compliance_engine import (
    compliance_engine, ComplianceStandard, ComplianceStatus, IPProtectionLevel
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compliance", tags=["Compliance & IP"])

class ComplianceAssessmentRequest(BaseModel):
    """Compliance Değerlendirme İsteği"""
    standards: List[str] = Field(..., description="Değerlendirilecek standartlar")

class ModuleAccessRequest(BaseModel):
    """Modül Erişim İsteği"""
    module_id: str = Field(..., description="Modül ID")
    user_license: Optional[str] = Field(None, description="Kullanıcı lisans anahtarı")

class ComplianceReportResponse(BaseModel):
    """Compliance Rapor Yanıtı"""
    success: bool
    report_id: str
    overall_status: str
    compliance_score: float
    standards: List[str]
    recommendations: List[str]
    message: str

class ModuleAccessResponse(BaseModel):
    """Modül Erişim Yanıtı"""
    success: bool
    module_id: str
    access_granted: bool
    message: str
    module_info: Optional[Dict[str, Any]] = None

@router.get("/health")
async def compliance_health():
    """Compliance servis sağlık kontrolü"""
    status_info = compliance_engine.get_compliance_status()
    
    return {
        "status": "healthy",
        "service": "Compliance Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "compliance_status": status_info
    }

@router.post("/assess", response_model=ComplianceReportResponse)
async def run_compliance_assessment(request: ComplianceAssessmentRequest):
    """Compliance değerlendirmesi çalıştır"""
    try:
        logger.info(f"Compliance değerlendirmesi başlatılıyor - Standartlar: {request.standards}")
        
        # Standartları dönüştür
        standards = []
        for standard_str in request.standards:
            try:
                standard = ComplianceStandard(standard_str)
                standards.append(standard)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Geçersiz standart: {standard_str}"
                )
        
        # Compliance değerlendirmesi çalıştır
        report = compliance_engine.run_compliance_assessment(standards)
        
        return ComplianceReportResponse(
            success=True,
            report_id=report.report_id,
            overall_status=report.overall_status.value,
            compliance_score=report.compliance_score,
            standards=[s.value for s in report.standards],
            recommendations=report.recommendations,
            message="Compliance değerlendirmesi başarıyla tamamlandı"
        )
        
    except Exception as e:
        logger.error(f"Compliance değerlendirmesi hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance değerlendirmesi başarısız: {str(e)}"
        )

@router.get("/report/{report_id}")
async def get_compliance_report(report_id: str):
    """Compliance raporu getir"""
    try:
        report_data = compliance_engine.generate_compliance_report(report_id)
        
        if not report_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance raporu bulunamadı"
            )
        
        return {
            "success": True,
            "report_id": report_id,
            "report_data": report_data,
            "message": "Compliance raporu başarıyla alındı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance raporu alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance raporu alınamadı: {str(e)}"
        )

@router.get("/reports")
async def get_compliance_reports():
    """Tüm compliance raporlarını getir"""
    try:
        reports = []
        
        for report_id, report in compliance_engine.compliance_reports.items():
            reports.append({
                "report_id": report_id,
                "report_date": report.report_date.isoformat(),
                "standards": [s.value for s in report.standards],
                "overall_status": report.overall_status.value,
                "compliance_score": report.compliance_score,
                "recommendations_count": len(report.recommendations)
            })
        
        # Tarihe göre sırala (en yeni önce)
        reports.sort(key=lambda x: x["report_date"], reverse=True)
        
        return {
            "success": True,
            "reports": reports,
            "count": len(reports),
            "message": f"{len(reports)} compliance raporu bulundu"
        }
        
    except Exception as e:
        logger.error(f"Compliance raporları alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance raporları alınamadı: {str(e)}"
        )

@router.get("/standards")
async def get_compliance_standards():
    """Mevcut compliance standartlarını getir"""
    try:
        standards = [
            {
                "standard": standard.value,
                "name": _get_standard_name(standard),
                "description": _get_standard_description(standard)
            }
            for standard in ComplianceStandard
        ]
        
        return {
            "success": True,
            "standards": standards,
            "count": len(standards),
            "message": "Compliance standartları başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Compliance standartları alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance standartları alınamadı: {str(e)}"
        )

@router.get("/checklists")
async def get_compliance_checklists():
    """Compliance checklist'lerini getir"""
    try:
        checklists = []
        
        for checklist in compliance_engine.compliance_checklists.values():
            checklists.append({
                "checklist_id": checklist.checklist_id,
                "standard": checklist.standard.value,
                "title": checklist.title,
                "description": checklist.description,
                "requirements_count": len(checklist.requirements),
                "status": checklist.status.value,
                "compliance_score": checklist.compliance_score,
                "last_assessment": checklist.last_assessment.isoformat() if checklist.last_assessment else None
            })
        
        return {
            "success": True,
            "checklists": checklists,
            "count": len(checklists),
            "message": "Compliance checklist'leri başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Compliance checklist'leri alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance checklist'leri alınamadı: {str(e)}"
        )

@router.get("/checklist/{checklist_id}")
async def get_compliance_checklist(checklist_id: str):
    """Belirli compliance checklist'ini getir"""
    try:
        if checklist_id not in compliance_engine.compliance_checklists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance checklist bulunamadı"
            )
        
        checklist = compliance_engine.compliance_checklists[checklist_id]
        
        return {
            "success": True,
            "checklist_id": checklist_id,
            "checklist": {
                "checklist_id": checklist.checklist_id,
                "standard": checklist.standard.value,
                "title": checklist.title,
                "description": checklist.description,
                "requirements": checklist.requirements,
                "status": checklist.status.value,
                "compliance_score": checklist.compliance_score,
                "last_assessment": checklist.last_assessment.isoformat() if checklist.last_assessment else None
            },
            "message": "Compliance checklist başarıyla alındı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance checklist alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance checklist alınamadı: {str(e)}"
        )

@router.post("/module-access", response_model=ModuleAccessResponse)
async def check_module_access(request: ModuleAccessRequest):
    """Modül erişim kontrolü"""
    try:
        logger.info(f"Modül erişim kontrolü - Modül: {request.module_id}")
        
        # Modül erişim kontrolü
        access_granted, message = compliance_engine.check_module_access(
            request.module_id, 
            request.user_license
        )
        
        # Modül bilgilerini al
        module_info = None
        if request.module_id in compliance_engine.patented_modules:
            module = compliance_engine.patented_modules[request.module_id]
            module_info = {
                "module_id": module.module_id,
                "module_name": module.module_name,
                "protection_level": module.protection_level.value,
                "patent_number": module.patent_number,
                "is_locked": module.is_locked,
                "access_restrictions": module.access_restrictions,
                "metadata": module.metadata
            }
        
        return ModuleAccessResponse(
            success=True,
            module_id=request.module_id,
            access_granted=access_granted,
            message=message,
            module_info=module_info
        )
        
    except Exception as e:
        logger.error(f"Modül erişim kontrolü hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Modül erişim kontrolü başarısız: {str(e)}"
        )

@router.get("/patented-modules")
async def get_patented_modules():
    """Patentli modülleri getir"""
    try:
        modules = compliance_engine.get_patented_modules()
        
        return {
            "success": True,
            "patented_modules": modules,
            "count": len(modules),
            "locked_count": sum(1 for m in modules if m["is_locked"]),
            "message": f"{len(modules)} patentli modül bulundu"
        }
        
    except Exception as e:
        logger.error(f"Patentli modüller alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Patentli modüller alınamadı: {str(e)}"
        )

@router.get("/module/{module_id}")
async def get_patented_module(module_id: str):
    """Belirli patentli modülü getir"""
    try:
        if module_id not in compliance_engine.patented_modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patentli modül bulunamadı"
            )
        
        module = compliance_engine.patented_modules[module_id]
        
        return {
            "success": True,
            "module_id": module_id,
            "module": {
                "module_id": module.module_id,
                "module_name": module.module_name,
                "protection_level": module.protection_level.value,
                "patent_number": module.patent_number,
                "is_locked": module.is_locked,
                "access_restrictions": module.access_restrictions,
                "metadata": module.metadata
            },
            "message": "Patentli modül başarıyla alındı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Patentli modül alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Patentli modül alınamadı: {str(e)}"
        )

@router.get("/protection-levels")
async def get_protection_levels():
    """IP koruma seviyelerini getir"""
    try:
        protection_levels = [
            {
                "level": level.value,
                "name": _get_protection_level_name(level),
                "description": _get_protection_level_description(level)
            }
            for level in IPProtectionLevel
        ]
        
        return {
            "success": True,
            "protection_levels": protection_levels,
            "count": len(protection_levels),
            "message": "IP koruma seviyeleri başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"IP koruma seviyeleri alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"IP koruma seviyeleri alınamadı: {str(e)}"
        )

@router.get("/status")
async def get_compliance_status():
    """Compliance durumunu getir"""
    try:
        status_info = compliance_engine.get_compliance_status()
        
        return {
            "success": True,
            "compliance_status": status_info,
            "message": "Compliance durumu başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Compliance durumu alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance durumu alınamadı: {str(e)}"
        )

# Helper functions
def _get_standard_name(standard: ComplianceStandard) -> str:
    """Standart ismini getir"""
    names = {
        ComplianceStandard.CE_MDR: "CE Medical Device Regulation",
        ComplianceStandard.ISO_13485: "ISO 13485 Quality Management System",
        ComplianceStandard.FDA_510K: "FDA 510(k) Premarket Notification",
        ComplianceStandard.HIPAA: "Health Insurance Portability and Accountability Act",
        ComplianceStandard.GDPR: "General Data Protection Regulation"
    }
    return names.get(standard, standard.value)

def _get_standard_description(standard: ComplianceStandard) -> str:
    """Standart açıklamasını getir"""
    descriptions = {
        ComplianceStandard.CE_MDR: "European Medical Device Regulation compliance requirements",
        ComplianceStandard.ISO_13485: "Quality management system for medical devices",
        ComplianceStandard.FDA_510K: "FDA premarket notification for medical devices",
        ComplianceStandard.HIPAA: "Health information privacy and security standards",
        ComplianceStandard.GDPR: "European data protection and privacy regulation"
    }
    return descriptions.get(standard, "")

def _get_protection_level_name(level: IPProtectionLevel) -> str:
    """Koruma seviyesi ismini getir"""
    names = {
        IPProtectionLevel.PUBLIC: "Public",
        IPProtectionLevel.PROTECTED: "Protected",
        IPProtectionLevel.CONFIDENTIAL: "Confidential",
        IPProtectionLevel.PATENTED: "Patented"
    }
    return names.get(level, level.value)

def _get_protection_level_description(level: IPProtectionLevel) -> str:
    """Koruma seviyesi açıklamasını getir"""
    descriptions = {
        IPProtectionLevel.PUBLIC: "Public domain - no restrictions",
        IPProtectionLevel.PROTECTED: "Protected intellectual property",
        IPProtectionLevel.CONFIDENTIAL: "Confidential and proprietary",
        IPProtectionLevel.PATENTED: "Patented technology with legal protection"
    }
    return descriptions.get(level, "")

# Test endpoint
@router.get("/test")
async def test_compliance_engine():
    """Compliance engine test"""
    try:
        # Compliance değerlendirmesi test et
        standards = [ComplianceStandard.CE_MDR, ComplianceStandard.ISO_13485]
        report = compliance_engine.run_compliance_assessment(standards)
        
        # Modül erişim test et
        access_ok, message = compliance_engine.check_module_access("suv_trend_001")
        
        # Patentli modülleri al
        modules = compliance_engine.get_patented_modules()
        
        return {
            "success": True,
            "test_results": {
                "compliance_report_id": report.report_id,
                "compliance_score": report.compliance_score,
                "overall_status": report.overall_status.value,
                "module_access_granted": access_ok,
                "module_access_message": message,
                "patented_modules_count": len(modules)
            },
            "message": "Compliance engine test başarılı"
        }
        
    except Exception as e:
        logger.error(f"Compliance engine test hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance engine test başarısız: {str(e)}"
        )
