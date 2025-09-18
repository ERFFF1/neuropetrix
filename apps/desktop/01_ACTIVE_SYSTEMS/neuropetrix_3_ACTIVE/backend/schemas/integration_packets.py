"""
NeuroPETrix v2.0 - Integration Packet Schemas
Veri akışı için standart paket yapıları
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUM TANIMLARI
# ============================================================================

class ClinicalGoal(str, Enum):
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    PROGNOSIS = "prognosis"
    FOLLOW_UP = "follow_up"

class WorkflowMode(str, Enum):
    DESKTOP = "desktop"
    WEB_BRIDGE = "web_bridge"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# ============================================================================
# TEMEL VERİ MODELLERİ
# ============================================================================

class PatientDemographics(BaseModel):
    patient_id: str = Field(..., description="Hasta kimlik numarası")
    name: str = Field(..., description="Hasta adı")
    age: int = Field(..., description="Yaş")
    gender: str = Field(..., description="Cinsiyet")
    weight: Optional[float] = Field(None, description="Kilo (kg)")
    height: Optional[float] = Field(None, description="Boy (cm)")
    
class LaboratoryData(BaseModel):
    hb: Optional[float] = Field(None, description="Hemoglobin")
    wbc: Optional[float] = Field(None, description="White Blood Cell")
    plt: Optional[float] = Field(None, description="Platelet")
    ldh: Optional[float] = Field(None, description="Lactate Dehydrogenase")
    cea: Optional[float] = Field(None, description="Carcinoembryonic Antigen")
    ca199: Optional[float] = Field(None, description="CA 19-9")
    psa: Optional[float] = Field(None, description="Prostate Specific Antigen")
    troponin: Optional[float] = Field(None, description="Troponin")
    bnp: Optional[float] = Field(None, description="Brain Natriuretic Peptide")
    creatinine: Optional[float] = Field(None, description="Creatinine")
    egfr: Optional[float] = Field(None, description="eGFR")

class ClinicalData(BaseModel):
    ecog_score: Optional[int] = Field(None, description="ECOG Performance Score")
    comorbidities: List[str] = Field(default_factory=list, description="Komorbiditeler")
    current_medications: List[str] = Field(default_factory=list, description="Mevcut ilaçlar")
    allergies: List[str] = Field(default_factory=list, description="Alerjiler")
    family_history: List[str] = Field(default_factory=list, description="Aile öyküsü")

# ============================================================================
# ENTEGRASYON PAKETLERİ
# ============================================================================

class PatientPacket(BaseModel):
    """HBYS'den çekilen tüm hasta verisi"""
    demographics: PatientDemographics
    laboratory: LaboratoryData
    clinical: ClinicalData
    icd_codes: List[str] = Field(..., description="ICD-10 kodları")
    branch: str = Field(..., description="Branş (Onkoloji, Radyoloji, vb.)")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "demographics": {
                    "patient_id": "P001",
                    "name": "Ahmet Yılmaz",
                    "age": 65,
                    "gender": "M",
                    "weight": 75.5,
                    "height": 175.0
                },
                "laboratory": {
                    "hb": 13.2,
                    "wbc": 8.5,
                    "plt": 250,
                    "ldh": 180
                },
                "clinical": {
                    "ecog_score": 1,
                    "comorbidities": ["Hipertansiyon", "Diyabet"],
                    "current_medications": ["Metformin", "Lisinopril"],
                    "allergies": ["Penicillin"],
                    "family_history": ["Baba: Akciğer kanseri"]
                },
                "icd_codes": ["C34.9", "I10"],
                "branch": "Onkoloji"
            }
        }

class CaseMeta(BaseModel):
    """DICOM ve PICO'ya özel meta veriler"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    patient_id: str = Field(..., description="Hasta kimlik numarası")
    clinical_goal: ClinicalGoal = Field(..., description="Klinik hedef")
    workflow_mode: WorkflowMode = Field(default=WorkflowMode.DESKTOP, description="Çalışma kipi")
    dicom_files: List[str] = Field(default_factory=list, description="DICOM dosya yolları")
    dicom_metadata: Dict[str, Any] = Field(default_factory=dict, description="DICOM meta verileri")
    pico_question: Optional[str] = Field(None, description="Oluşturulan PICO sorusu")
    pico_components: Dict[str, str] = Field(default_factory=dict, description="PICO bileşenleri")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "C001",
                "patient_id": "P001",
                "clinical_goal": "diagnosis",
                "workflow_mode": "desktop",
                "dicom_files": ["/path/to/dicom1.dcm", "/path/to/dicom2.dcm"],
                "pico_question": "C34.9 tanılı hastalarda tanı kararı için uygun yaklaşım standart yöntemler ile karşılaştırıldığında klinik sonuçlar açısından etkili midir?",
                "pico_components": {
                    "P": "C34.9 tanılı hastalar",
                    "I": "Tanı kararı için uygun yaklaşım",
                    "C": "Standart yöntemler",
                    "O": "Klinik sonuçlar"
                }
            }
        }

class EvidencePacket(BaseModel):
    """PICO, GRADE ve literatür verileri"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    pico_question: str = Field(..., description="PICO sorusu")
    search_strategy: Dict[str, Any] = Field(..., description="Arama stratejisi")
    literature_results: List[Dict[str, Any]] = Field(default_factory=list, description="Literatür sonuçları")
    grade_assessment: Dict[str, Any] = Field(default_factory=dict, description="GRADE değerlendirmesi")
    evidence_summary: str = Field(..., description="Kanıt özeti")
    recommendations: List[str] = Field(default_factory=list, description="Öneriler")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "C001",
                "pico_question": "C34.9 tanılı hastalarda tanı kararı için uygun yaklaşım standart yöntemler ile karşılaştırıldığında klinik sonuçlar açısından etkili midir?",
                "search_strategy": {
                    "databases": ["PubMed", "Embase", "Cochrane"],
                    "keywords": ["lung cancer", "diagnosis", "PET-CT"],
                    "date_range": "2019-2024"
                },
                "literature_results": [
                    {
                        "title": "PET-CT in Lung Cancer Diagnosis",
                        "authors": "Smith J, et al.",
                        "journal": "J Nucl Med",
                        "year": 2023,
                        "doi": "10.1000/example",
                        "grade": "A",
                        "relevance": "High"
                    }
                ],
                "grade_assessment": {
                    "overall_grade": "A",
                    "quality": "High",
                    "consistency": "Consistent",
                    "directness": "Direct",
                    "precision": "Precise"
                },
                "evidence_summary": "PET-CT shows high accuracy in lung cancer diagnosis with sensitivity 95% and specificity 88%.",
                "recommendations": [
                    "PET-CT should be used as first-line imaging for suspected lung cancer",
                    "Combined with clinical assessment for optimal diagnostic accuracy"
                ]
            }
        }

class ImagingMetrics(BaseModel):
    """MONAI ve PyRadiomics çıktıları"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    segmentation_results: Dict[str, Any] = Field(..., description="Segmentasyon sonuçları")
    radiomics_features: Dict[str, Any] = Field(..., description="Radyomik özellikler")
    suv_measurements: Dict[str, float] = Field(..., description="SUV ölçümleri")
    percist_score: Optional[str] = Field(None, description="PERCIST skoru")
    deauville_score: Optional[str] = Field(None, description="Deauville skoru")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "C001",
                "segmentation_results": {
                    "lesion_count": 3,
                    "total_volume": 45.2,
                    "segmentation_quality": "excellent",
                    "manual_corrections": 0
                },
                "radiomics_features": {
                    "firstorder": {
                        "mean": 2.45,
                        "std": 0.89,
                        "skewness": 0.12
                    },
                    "shape": {
                        "volume": 45.2,
                        "surface_area": 67.8,
                        "sphericity": 0.78
                    },
                    "glcm": {
                        "energy": 0.023,
                        "contrast": 0.156,
                        "correlation": 0.789
                    }
                },
                "suv_measurements": {
                    "suvmax": 8.9,
                    "suvmean": 5.2,
                    "suvpeak": 7.8,
                    "mtv": 45.2,
                    "tlg": 235.0
                },
                "percist_score": "PR",
                "deauville_score": "3"
            }
        }

class DecisionPacket(BaseModel):
    """AI karar ve öneri paketi"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    clinical_goal: ClinicalGoal = Field(..., description="Klinik hedef")
    evidence_summary: str = Field(..., description="Kanıt özeti")
    imaging_findings: str = Field(..., description="Görüntüleme bulguları")
    ai_conclusion: str = Field(..., description="AI sonucu - kısa ve eylem odaklı")
    recommendations: List[str] = Field(..., description="Detaylı öneriler")
    risk_benefit: Dict[str, str] = Field(..., description="Risk-fayda analizi")
    contraindications: List[str] = Field(default_factory=list, description="Kontrendikasyonlar")
    applicability_score: float = Field(..., description="Uygulanabilirlik skoru (0-1)")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "C001",
                "clinical_goal": "diagnosis",
                "evidence_summary": "PET-CT shows high accuracy in lung cancer diagnosis with strong evidence (Grade A).",
                "imaging_findings": "3 lesions detected with SUVmax 8.9, total volume 45.2cc. PERCIST score: PR.",
                "ai_conclusion": "PET-CT confirms lung cancer diagnosis with high confidence. Recommend immediate biopsy for tissue confirmation.",
                "recommendations": [
                    "Proceed with tissue biopsy for definitive diagnosis",
                    "Consider staging with additional imaging if needed",
                    "Refer to oncology for treatment planning"
                ],
                "risk_benefit": {
                    "benefits": "High diagnostic accuracy, non-invasive, comprehensive staging",
                    "risks": "Radiation exposure, false positive rate 12%"
                },
                "contraindications": ["Pregnancy", "Severe claustrophobia"],
                "applicability_score": 0.92
            }
        }

class ReportPacket(BaseModel):
    """TSNM rapor ve Evidence Annex paketi"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    tsnm_report: Dict[str, Any] = Field(..., description="TSNM klinik raporu")
    evidence_annex: Dict[str, Any] = Field(..., description="Evidence Annex")
    fhir_diagnostic_report: Dict[str, Any] = Field(..., description="FHIR DiagnosticReport")
    fhir_document_reference: Dict[str, Any] = Field(..., description="FHIR DocumentReference")
    report_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "case_id": "C001",
                "tsnm_report": {
                    "patient_info": "Ahmet Yılmaz, 65M",
                    "clinical_history": "Suspected lung cancer",
                    "technique": "18F-FDG PET-CT",
                    "findings": "3 FDG-avid lesions in right lung",
                    "impression": "Findings consistent with primary lung cancer",
                    "recommendations": "Biopsy for tissue confirmation"
                },
                "evidence_annex": {
                    "pico_question": "C34.9 tanılı hastalarda tanı kararı için uygun yaklaşım...",
                    "grade_assessment": "Grade A evidence",
                    "literature_references": ["Smith J, et al. J Nucl Med 2023"],
                    "clinical_decision_support": "AI recommendation: Proceed with biopsy"
                },
                "fhir_diagnostic_report": {
                    "resourceType": "DiagnosticReport",
                    "status": "final",
                    "code": {"coding": [{"system": "http://loinc.org", "code": "68633-1"}]}
                },
                "fhir_document_reference": {
                    "resourceType": "DocumentReference",
                    "status": "current",
                    "type": {"coding": [{"system": "http://loinc.org", "code": "11506-3"}]}
                }
            }
        }

# ============================================================================
# WORKFLOW ENTEGRASYON MODELLERİ
# ============================================================================

class WorkflowIntegration(BaseModel):
    """Ana workflow entegrasyon modeli"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    workflow_mode: WorkflowMode = Field(..., description="Çalışma kipi")
    current_step: str = Field(..., description="Mevcut adım")
    next_step: str = Field(..., description="Sonraki adım")
    dependencies: List[str] = Field(default_factory=list, description="Bağımlılıklar")
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class IntegrationStatus(BaseModel):
    """Entegrasyon durumu takibi"""
    case_id: str = Field(..., description="Vaka kimlik numarası")
    patient_packet: bool = Field(default=False, description="Patient packet hazır mı?")
    case_meta: bool = Field(default=False, description="Case meta hazır mı?")
    evidence_packet: bool = Field(default=False, description="Evidence packet hazır mı?")
    imaging_metrics: bool = Field(default=False, description="Imaging metrics hazır mı?")
    decision_packet: bool = Field(default=False, description="Decision packet hazır mı?")
    report_packet: bool = Field(default=False, description="Report packet hazır mı?")
    overall_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_integration_packet(
    case_id: str,
    patient_data: dict,
    clinical_goal: ClinicalGoal,
    workflow_mode: WorkflowMode = WorkflowMode.DESKTOP
) -> Dict[str, Any]:
    """Entegrasyon paketlerini oluşturur"""
    
    # Patient Packet
    patient_packet = PatientPacket(
        demographics=PatientDemographics(**patient_data.get("demographics", {})),
        laboratory=LaboratoryData(**patient_data.get("laboratory", {})),
        clinical=ClinicalData(**patient_data.get("clinical", {})),
        icd_codes=patient_data.get("icd_codes", []),
        branch=patient_data.get("branch", "Genel")
    )
    
    # Case Meta
    case_meta = CaseMeta(
        case_id=case_id,
        patient_id=patient_packet.demographics.patient_id,
        clinical_goal=clinical_goal,
        workflow_mode=workflow_mode
    )
    
    return {
        "patient_packet": patient_packet.dict(),
        "case_meta": case_meta.dict(),
        "integration_status": IntegrationStatus(
            case_id=case_id,
            patient_packet=True,
            case_meta=True
        ).dict()
    }

def validate_integration_packet(packet_data: dict) -> bool:
    """Entegrasyon paketinin geçerliliğini kontrol eder"""
    try:
        # Gerekli alanları kontrol et
        required_fields = ["case_id", "patient_packet", "case_meta"]
        for field in required_fields:
            if field not in packet_data:
                return False
        
        # Veri tiplerini kontrol et
        if not isinstance(packet_data["case_id"], str):
            return False
            
        return True
    except Exception:
        return False

# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "PatientPacket",
    "CaseMeta", 
    "EvidencePacket",
    "ImagingMetrics",
    "DecisionPacket",
    "ReportPacket",
    "WorkflowIntegration",
    "IntegrationStatus",
    "ClinicalGoal",
    "WorkflowMode",
    "ProcessingStatus",
    "create_integration_packet",
    "validate_integration_packet"
]
