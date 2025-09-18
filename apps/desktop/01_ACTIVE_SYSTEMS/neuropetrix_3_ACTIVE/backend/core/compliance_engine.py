"""
Compliance Engine - CE-MDR/ISO 13485 Checklist & Patentli Modül Kilitleme
Compliance Reporter ve IP koruması
"""

import logging
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    """Compliance Standartları"""
    CE_MDR = "CE-MDR"  # Medical Device Regulation
    ISO_13485 = "ISO-13485"  # Quality Management System
    FDA_510K = "FDA-510K"  # FDA Premarket Notification
    HIPAA = "HIPAA"  # Health Insurance Portability and Accountability Act
    GDPR = "GDPR"  # General Data Protection Regulation

class ComplianceStatus(Enum):
    """Compliance Durumu"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANT = "partial_compliant"
    NOT_ASSESSED = "not_assessed"

class IPProtectionLevel(Enum):
    """IP Koruma Seviyesi"""
    PUBLIC = "public"
    PROTECTED = "protected"
    CONFIDENTIAL = "confidential"
    PATENTED = "patented"

@dataclass
class ComplianceChecklist:
    """Compliance Checklist"""
    checklist_id: str
    standard: ComplianceStandard
    title: str
    description: str
    requirements: List[Dict[str, Any]] = field(default_factory=list)
    status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED
    last_assessment: Optional[datetime] = None
    compliance_score: float = 0.0

@dataclass
class ComplianceReport:
    """Compliance Raporu"""
    report_id: str
    report_date: datetime
    standards: List[ComplianceStandard]
    overall_status: ComplianceStatus
    compliance_score: float
    checklists: List[ComplianceChecklist]
    recommendations: List[str] = field(default_factory=list)
    next_assessment: Optional[datetime] = None

@dataclass
class PatentedModule:
    """Patentli Modül"""
    module_id: str
    module_name: str
    protection_level: IPProtectionLevel
    patent_number: Optional[str] = None
    license_key: Optional[str] = None
    is_locked: bool = False
    access_restrictions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ComplianceEngine:
    """Compliance Motoru"""
    
    def __init__(self):
        self.compliance_checklists: Dict[str, ComplianceChecklist] = {}
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        self.patented_modules: Dict[str, PatentedModule] = {}
        
        # Compliance checklist'leri yükle
        self._load_compliance_checklists()
        
        # Patentli modülleri yükle
        self._load_patented_modules()
        
        logger.info("Compliance Engine başlatıldı")

    def _load_compliance_checklists(self):
        """Compliance checklist'leri yükle"""
        # CE-MDR Checklist
        ce_mdr_checklist = ComplianceChecklist(
            checklist_id="ce_mdr_001",
            standard=ComplianceStandard.CE_MDR,
            title="CE-MDR Medical Device Regulation Compliance",
            description="European Medical Device Regulation compliance checklist",
            requirements=[
                {
                    "id": "ce_mdr_001",
                    "title": "Clinical Evaluation",
                    "description": "Clinical evaluation of the medical device",
                    "required": True,
                    "weight": 0.3
                },
                {
                    "id": "ce_mdr_002",
                    "title": "Risk Management",
                    "description": "Risk management system implementation",
                    "required": True,
                    "weight": 0.25
                },
                {
                    "id": "ce_mdr_003",
                    "title": "Quality Management System",
                    "description": "ISO 13485 compliant QMS",
                    "required": True,
                    "weight": 0.2
                },
                {
                    "id": "ce_mdr_004",
                    "title": "Post-Market Surveillance",
                    "description": "Post-market surveillance system",
                    "required": True,
                    "weight": 0.15
                },
                {
                    "id": "ce_mdr_005",
                    "title": "Technical Documentation",
                    "description": "Complete technical documentation",
                    "required": True,
                    "weight": 0.1
                }
            ]
        )
        
        # ISO 13485 Checklist
        iso_13485_checklist = ComplianceChecklist(
            checklist_id="iso_13485_001",
            standard=ComplianceStandard.ISO_13485,
            title="ISO 13485 Quality Management System",
            description="ISO 13485 Quality Management System for Medical Devices",
            requirements=[
                {
                    "id": "iso_13485_001",
                    "title": "Management Responsibility",
                    "description": "Management commitment and responsibility",
                    "required": True,
                    "weight": 0.2
                },
                {
                    "id": "iso_13485_002",
                    "title": "Resource Management",
                    "description": "Human resources and infrastructure",
                    "required": True,
                    "weight": 0.15
                },
                {
                    "id": "iso_13485_003",
                    "title": "Product Realization",
                    "description": "Product design and development process",
                    "required": True,
                    "weight": 0.25
                },
                {
                    "id": "iso_13485_004",
                    "title": "Measurement, Analysis and Improvement",
                    "description": "Monitoring and measurement processes",
                    "required": True,
                    "weight": 0.2
                },
                {
                    "id": "iso_13485_005",
                    "title": "Documentation Control",
                    "description": "Document control and records management",
                    "required": True,
                    "weight": 0.2
                }
            ]
        )
        
        self.compliance_checklists["ce_mdr_001"] = ce_mdr_checklist
        self.compliance_checklists["iso_13485_001"] = iso_13485_checklist

    def _load_patented_modules(self):
        """Patentli modülleri yükle"""
        # SUV Trend Modülü
        suv_trend_module = PatentedModule(
            module_id="suv_trend_001",
            module_name="SUV Trend Analysis",
            protection_level=IPProtectionLevel.PATENTED,
            patent_number="US20240000001A1",
            license_key=self._generate_license_key("suv_trend_001"),
            is_locked=True,
            access_restrictions=["licensed_users_only", "encrypted_access"],
            metadata={
                "description": "Advanced SUV trend analysis with PERCIST compliance",
                "version": "2.0.0",
                "patent_filing_date": "2024-01-01",
                "patent_holder": "NeuroPETRIX Technologies"
            }
        )
        
        # Evidence Annex Modülü
        evidence_annex_module = PatentedModule(
            module_id="evidence_annex_001",
            module_name="Evidence Annex Generator",
            protection_level=IPProtectionLevel.PATENTED,
            patent_number="US20240000002A1",
            license_key=self._generate_license_key("evidence_annex_001"),
            is_locked=True,
            access_restrictions=["licensed_users_only", "encrypted_access"],
            metadata={
                "description": "Automated evidence annex generation for clinical reports",
                "version": "1.5.0",
                "patent_filing_date": "2024-01-15",
                "patent_holder": "NeuroPETRIX Technologies"
            }
        )
        
        # AI Clinical Interpretation Modülü
        ai_interpretation_module = PatentedModule(
            module_id="ai_interpretation_001",
            module_name="AI Clinical Interpretation",
            protection_level=IPProtectionLevel.CONFIDENTIAL,
            license_key=self._generate_license_key("ai_interpretation_001"),
            is_locked=True,
            access_restrictions=["confidential_access"],
            metadata={
                "description": "AI-powered clinical interpretation with multi-model integration",
                "version": "3.0.0",
                "confidentiality_level": "high",
                "owner": "NeuroPETRIX Technologies"
            }
        )
        
        self.patented_modules["suv_trend_001"] = suv_trend_module
        self.patented_modules["evidence_annex_001"] = evidence_annex_module
        self.patented_modules["ai_interpretation_001"] = ai_interpretation_module

    def _generate_license_key(self, module_id: str) -> str:
        """Lisans anahtarı oluştur"""
        timestamp = datetime.now().isoformat()
        raw_key = f"{module_id}_{timestamp}_neuropetrix"
        return hashlib.sha256(raw_key.encode()).hexdigest()[:32]

    def run_compliance_assessment(self, standards: List[ComplianceStandard]) -> ComplianceReport:
        """Compliance değerlendirmesi çalıştır"""
        logger.info(f"Compliance değerlendirmesi başlatılıyor - Standartlar: {[s.value for s in standards]}")
        
        report_id = f"comp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        assessed_checklists = []
        total_score = 0.0
        compliant_count = 0
        
        for standard in standards:
            # Standard'a ait checklist'i bul
            checklist = self._find_checklist_by_standard(standard)
            if checklist:
                # Checklist'i değerlendir
                assessed_checklist = self._assess_checklist(checklist)
                assessed_checklists.append(assessed_checklist)
                
                total_score += assessed_checklist.compliance_score
                if assessed_checklist.status == ComplianceStatus.COMPLIANT:
                    compliant_count += 1
        
        # Genel durum belirleme
        if compliant_count == len(assessed_checklists):
            overall_status = ComplianceStatus.COMPLIANT
        elif compliant_count > 0:
            overall_status = ComplianceStatus.PARTIAL_COMPLIANT
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        # Genel compliance skoru
        overall_score = total_score / len(assessed_checklists) if assessed_checklists else 0.0
        
        # Öneriler oluştur
        recommendations = self._generate_compliance_recommendations(assessed_checklists)
        
        # Sonraki değerlendirme tarihi
        next_assessment = datetime.now() + timedelta(days=90)  # 3 ay sonra
        
        # Compliance raporu oluştur
        compliance_report = ComplianceReport(
            report_id=report_id,
            report_date=datetime.now(),
            standards=standards,
            overall_status=overall_status,
            compliance_score=overall_score,
            checklists=assessed_checklists,
            recommendations=recommendations,
            next_assessment=next_assessment
        )
        
        # Raporu kaydet
        self.compliance_reports[report_id] = compliance_report
        
        logger.info(f"Compliance değerlendirmesi tamamlandı - Rapor ID: {report_id}")
        return compliance_report

    def _find_checklist_by_standard(self, standard: ComplianceStandard) -> Optional[ComplianceChecklist]:
        """Standard'a göre checklist bul"""
        for checklist in self.compliance_checklists.values():
            if checklist.standard == standard:
                return checklist
        return None

    def _assess_checklist(self, checklist: ComplianceChecklist) -> ComplianceChecklist:
        """Checklist'i değerlendir"""
        # Mock değerlendirme - gerçek implementasyonda sistem durumu kontrol edilir
        total_weight = sum(req.get("weight", 0) for req in checklist.requirements)
        compliance_score = 0.0
        compliant_requirements = 0
        
        for requirement in checklist.requirements:
            # Mock compliance check
            is_compliant = self._check_requirement_compliance(requirement)
            if is_compliant:
                compliant_requirements += 1
                compliance_score += requirement.get("weight", 0)
        
        # Compliance skorunu yüzdeye çevir
        if total_weight > 0:
            compliance_score = (compliance_score / total_weight) * 100
        
        # Durum belirleme
        if compliance_score >= 90:
            status = ComplianceStatus.COMPLIANT
        elif compliance_score >= 70:
            status = ComplianceStatus.PARTIAL_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        # Checklist'i güncelle
        checklist.status = status
        checklist.last_assessment = datetime.now()
        checklist.compliance_score = compliance_score
        
        return checklist

    def _check_requirement_compliance(self, requirement: Dict[str, Any]) -> bool:
        """Requirement compliance kontrolü (mock)"""
        # Gerçek implementasyonda sistem durumu kontrol edilir
        # Şimdilik mock olarak %80 olasılıkla compliant döndürüyoruz
        import random
        return random.random() > 0.2

    def _generate_compliance_recommendations(self, checklists: List[ComplianceChecklist]) -> List[str]:
        """Compliance önerileri oluştur"""
        recommendations = []
        
        for checklist in checklists:
            if checklist.status == ComplianceStatus.NON_COMPLIANT:
                recommendations.append(f"{checklist.standard.value}: Tam compliance sağlanmalı")
            elif checklist.status == ComplianceStatus.PARTIAL_COMPLIANT:
                recommendations.append(f"{checklist.standard.value}: Compliance iyileştirilmeli")
        
        # Genel öneriler
        recommendations.extend([
            "Düzenli compliance değerlendirmesi yapılmalı",
            "Risk yönetimi süreçleri güncellenmelidir",
            "Dokümantasyon sürekli güncel tutulmalıdır"
        ])
        
        return recommendations

    def check_module_access(self, module_id: str, user_license: Optional[str] = None) -> Tuple[bool, str]:
        """Modül erişim kontrolü"""
        if module_id not in self.patented_modules:
            return False, "Modül bulunamadı"
        
        module = self.patented_modules[module_id]
        
        if not module.is_locked:
            return True, "Modül erişilebilir"
        
        # Lisans kontrolü
        if module.license_key and user_license != module.license_key:
            return False, "Geçersiz lisans anahtarı"
        
        # Erişim kısıtlamaları kontrolü
        if "licensed_users_only" in module.access_restrictions and not user_license:
            return False, "Lisanslı kullanıcı erişimi gerekli"
        
        return True, "Modül erişilebilir"

    def get_patented_modules(self) -> List[Dict[str, Any]]:
        """Patentli modülleri getir"""
        modules = []
        
        for module in self.patented_modules.values():
            modules.append({
                "module_id": module.module_id,
                "module_name": module.module_name,
                "protection_level": module.protection_level.value,
                "patent_number": module.patent_number,
                "is_locked": module.is_locked,
                "access_restrictions": module.access_restrictions,
                "metadata": module.metadata
            })
        
        return modules

    def get_compliance_status(self) -> Dict[str, Any]:
        """Compliance durumunu getir"""
        total_reports = len(self.compliance_reports)
        recent_reports = [
            report for report in self.compliance_reports.values()
            if report.report_date > datetime.now() - timedelta(days=30)
        ]
        
        return {
            "total_reports": total_reports,
            "recent_reports": len(recent_reports),
            "patented_modules": len(self.patented_modules),
            "locked_modules": sum(1 for m in self.patented_modules.values() if m.is_locked),
            "last_assessment": max(
                [report.report_date for report in self.compliance_reports.values()],
                default=None
            ),
            "timestamp": datetime.now().isoformat()
        }

    def generate_compliance_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Compliance raporu oluştur"""
        if report_id not in self.compliance_reports:
            return None
        
        report = self.compliance_reports[report_id]
        
        return {
            "report_id": report.report_id,
            "report_date": report.report_date.isoformat(),
            "standards": [s.value for s in report.standards],
            "overall_status": report.overall_status.value,
            "compliance_score": report.compliance_score,
            "checklists": [
                {
                    "checklist_id": checklist.checklist_id,
                    "standard": checklist.standard.value,
                    "title": checklist.title,
                    "status": checklist.status.value,
                    "compliance_score": checklist.compliance_score,
                    "last_assessment": checklist.last_assessment.isoformat() if checklist.last_assessment else None
                }
                for checklist in report.checklists
            ],
            "recommendations": report.recommendations,
            "next_assessment": report.next_assessment.isoformat() if report.next_assessment else None
        }

# Global compliance engine instance
compliance_engine = ComplianceEngine()

# Kullanım örneği
if __name__ == "__main__":
    # Compliance değerlendirmesi çalıştır
    standards = [ComplianceStandard.CE_MDR, ComplianceStandard.ISO_13485]
    report = compliance_engine.run_compliance_assessment(standards)
    
    print(f"Compliance Raporu: {report.report_id}")
    print(f"Genel Durum: {report.overall_status.value}")
    print(f"Compliance Skoru: {report.compliance_score:.1f}%")
    print(f"Öneriler: {len(report.recommendations)}")
    
    # Modül erişim kontrolü
    access_ok, message = compliance_engine.check_module_access("suv_trend_001")
    print(f"SUV Trend Modülü Erişimi: {access_ok} - {message}")
    
    # Patentli modülleri listele
    modules = compliance_engine.get_patented_modules()
    print(f"Patentli Modüller: {len(modules)}")
