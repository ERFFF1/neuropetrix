"""
NeuroPETrix v2.0 - PICO → MONAI Integration Service
PICO'dan gelen purpose ve ICD bilgisi, MONAI'nin segmentasyonunu yönlendirir
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import uuid
from datetime import datetime

from ..schemas.integration_packets import (
    ClinicalGoal, CaseMeta, ImagingMetrics, 
    ProcessingStatus, create_integration_packet
)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PICO → MONAI INTEGRATION SERVICE
# ============================================================================

class PICOMONAIIntegrationService:
    """PICO ve MONAI arasında entegrasyon sağlar"""
    
    def __init__(self):
        self.segmentation_focus_areas = {
            "diagnosis": {
                "lung": ["lung", "mediastinum", "lymph_nodes"],
                "liver": ["liver", "bile_ducts", "gallbladder"],
                "brain": ["brain", "cerebellum", "brainstem"],
                "breast": ["breast", "axilla", "chest_wall"],
                "prostate": ["prostate", "seminal_vesicles", "pelvic_lymph_nodes"]
            },
            "treatment": {
                "lung": ["lung", "mediastinum", "lymph_nodes", "adrenal_glands"],
                "liver": ["liver", "bile_ducts", "gallbladder", "portal_vein"],
                "brain": ["brain", "cerebellum", "brainstem", "meninges"],
                "breast": ["breast", "axilla", "chest_wall", "internal_mammary"],
                "prostate": ["prostate", "seminal_vesicles", "pelvic_lymph_nodes", "bones"]
            },
            "prognosis": {
                "lung": ["lung", "mediastinum", "lymph_nodes", "bones", "adrenal_glands"],
                "liver": ["liver", "bile_ducts", "gallbladder", "portal_vein", "mesentery"],
                "brain": ["brain", "cerebellum", "brainstem", "meninges", "ventricles"],
                "breast": ["breast", "axilla", "chest_wall", "internal_mammary", "bones"],
                "prostate": ["prostate", "seminal_vesicles", "pelvic_lymph_nodes", "bones", "liver"]
            },
            "follow_up": {
                "lung": ["lung", "mediastinum", "lymph_nodes"],
                "liver": ["liver", "bile_ducts", "gallbladder"],
                "brain": ["brain", "cerebellum", "brainstem"],
                "breast": ["breast", "axilla", "chest_wall"],
                "prostate": ["prostate", "seminal_vesicles", "pelvic_lymph_nodes"]
            }
        }
        
        self.icd_organ_mapping = {
            "C34": "lung",           # Akciğer kanseri
            "C22": "liver",          # Karaciğer kanseri
            "C71": "brain",          # Beyin kanseri
            "C50": "breast",         # Meme kanseri
            "C61": "prostate",       # Prostat kanseri
            "C18": "colon",          # Kolon kanseri
            "C16": "stomach",        # Mide kanseri
            "C25": "pancreas",       # Pankreas kanseri
            "C67": "bladder",        # Mesane kanseri
            "C73": "thyroid"         # Tiroid kanseri
        }
        
        self.segmentation_parameters = {
            "diagnosis": {
                "sensitivity": 0.95,
                "specificity": 0.90,
                "min_lesion_size": 5.0,  # mm
                "max_lesion_size": 100.0,  # mm
                "segmentation_method": "adaptive_threshold"
            },
            "treatment": {
                "sensitivity": 0.98,
                "specificity": 0.95,
                "min_lesion_size": 3.0,  # mm
                "max_lesion_size": 150.0,  # mm
                "segmentation_method": "deep_learning"
            },
            "prognosis": {
                "sensitivity": 0.92,
                "specificity": 0.88,
                "min_lesion_size": 8.0,  # mm
                "max_lesion_size": 200.0,  # mm
                "segmentation_method": "hybrid"
            },
            "follow_up": {
                "sensitivity": 0.90,
                "specificity": 0.85,
                "min_lesion_size": 10.0,  # mm
                "max_lesion_size": 120.0,  # mm
                "segmentation_method": "threshold_based"
            }
        }
    
    def determine_segmentation_focus(
        self, 
        icd_codes: List[str], 
        clinical_goal: ClinicalGoal
    ) -> Dict[str, Any]:
        """ICD kodları ve klinik hedefe göre segmentasyon odak alanlarını belirler"""
        
        logger.info(f"Segmentasyon odak alanları belirleniyor: ICD={icd_codes}, Goal={clinical_goal}")
        
        # ICD kodlarından organ tespiti
        target_organs = []
        for icd_code in icd_codes:
            organ_prefix = icd_code[:3]
            if organ_prefix in self.icd_organ_mapping:
                target_organs.append(self.icd_organ_mapping[organ_prefix])
        
        if not target_organs:
            # Varsayılan olarak akciğer
            target_organs = ["lung"]
            logger.warning(f"ICD kodlarından organ tespit edilemedi, varsayılan: {target_organs}")
        
        # Klinik hedef için segmentasyon parametreleri
        goal_params = self.segmentation_parameters.get(clinical_goal.value, {})
        
        # Odak alanları
        focus_areas = {}
        for organ in target_organs:
            if organ in self.segmentation_focus_areas.get(clinical_goal.value, {}):
                focus_areas[organ] = self.segmentation_focus_areas[clinical_goal.value][organ]
        
        # Segmentasyon stratejisi
        segmentation_strategy = {
            "target_organs": target_organs,
            "focus_areas": focus_areas,
            "parameters": goal_params,
            "clinical_goal": clinical_goal.value,
            "priority": self._get_priority(clinical_goal),
            "estimated_time": self._estimate_processing_time(clinical_goal, len(target_organs))
        }
        
        logger.info(f"Segmentasyon stratejisi belirlendi: {segmentation_strategy}")
        return segmentation_strategy
    
    def _get_priority(self, clinical_goal: ClinicalGoal) -> str:
        """Klinik hedefe göre öncelik belirler"""
        priority_map = {
            ClinicalGoal.DIAGNOSIS: "high",
            ClinicalGoal.TREATMENT: "critical",
            ClinicalGoal.PROGNOSIS: "medium",
            ClinicalGoal.FOLLOW_UP: "low"
        }
        return priority_map.get(clinical_goal, "medium")
    
    def _estimate_processing_time(self, clinical_goal: ClinicalGoal, organ_count: int) -> int:
        """İşlem süresini tahmin eder (saniye)"""
        base_time = {
            ClinicalGoal.DIAGNOSIS: 120,
            ClinicalGoal.TREATMENT: 180,
            ClinicalGoal.PROGNOSIS: 150,
            ClinicalGoal.FOLLOW_UP: 90
        }
        
        organ_multiplier = 1 + (organ_count - 1) * 0.3
        return int(base_time.get(clinical_goal, 120) * organ_multiplier)
    
    def create_monai_config(
        self, 
        case_meta: CaseMeta,
        segmentation_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """MONAI için konfigürasyon dosyası oluşturur"""
        
        logger.info(f"MONAI konfigürasyonu oluşturuluyor: Case={case_meta.case_id}")
        
        monai_config = {
            "case_id": case_meta.case_id,
            "patient_id": case_meta.patient_id,
            "clinical_goal": case_meta.clinical_goal.value,
            "workflow_mode": case_meta.workflow_mode.value,
            "segmentation": {
                "target_organs": segmentation_strategy["target_organs"],
                "focus_areas": segmentation_strategy["focus_areas"],
                "parameters": segmentation_strategy["parameters"],
                "priority": segmentation_strategy["priority"],
                "estimated_time": segmentation_strategy["estimated_time"]
            },
            "input": {
                "dicom_files": case_meta.dicom_files,
                "dicom_metadata": case_meta.dicom_metadata
            },
            "output": {
                "segmentation_masks": f"output/{case_meta.case_id}/segmentation/",
                "radiomics_features": f"output/{case_meta.case_id}/radiomics/",
                "suv_measurements": f"output/{case_meta.case_id}/suv/",
                "reports": f"output/{case_meta.case_id}/reports/"
            },
            "processing": {
                "model_version": "v2.0",
                "gpu_required": True,
                "memory_requirement": "8GB",
                "batch_size": 1
            },
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        return monai_config
    
    def validate_monai_input(
        self, 
        case_meta: CaseMeta,
        segmentation_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """MONAI giriş verilerini doğrular"""
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # DICOM dosyaları kontrolü
        if not case_meta.dicom_files:
            validation_result["is_valid"] = False
            validation_result["errors"].append("DICOM dosyaları bulunamadı")
        else:
            # DICOM dosya boyutu kontrolü
            total_size = 0
            for dicom_file in case_meta.dicom_files:
                if Path(dicom_file).exists():
                    total_size += Path(dicom_file).stat().st_size
                else:
                    validation_result["warnings"].append(f"DICOM dosyası bulunamadı: {dicom_file}")
            
            # Boyut kontrolü (GB)
            size_gb = total_size / (1024**3)
            if size_gb > 2.0:
                validation_result["warnings"].append(f"Büyük DICOM veri seti: {size_gb:.2f} GB")
                validation_result["recommendations"].append("İşlem süresi uzun olabilir")
        
        # Organ sayısı kontrolü
        organ_count = len(segmentation_strategy.get("target_organs", []))
        if organ_count > 3:
            validation_result["warnings"].append(f"Çoklu organ segmentasyonu: {organ_count} organ")
            validation_result["recommendations"].append("İşlem süresi uzun olabilir")
        
        # Klinik hedef kontrolü
        if case_meta.clinical_goal == ClinicalGoal.TREATMENT:
            validation_result["recommendations"].append("Tedavi hedefi için yüksek hassasiyet modu önerilir")
        
        return validation_result
    
    def execute_monai_segmentation(
        self, 
        monai_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """MONAI segmentasyonunu başlatır (mock implementation)"""
        
        logger.info(f"MONAI segmentasyonu başlatılıyor: Case={monai_config['case_id']}")
        
        # Mock segmentasyon sonucu
        mock_result = {
            "case_id": monai_config["case_id"],
            "status": "processing",
            "progress": 0,
            "segmentation_results": {
                "lesion_count": 0,
                "total_volume": 0.0,
                "segmentation_quality": "pending",
                "manual_corrections": 0
            },
            "processing_info": {
                "started_at": datetime.now().isoformat(),
                "estimated_completion": None,
                "current_step": "initializing"
            }
        }
        
        # Gerçek implementasyonda burada MONAI çağrısı yapılır
        # subprocess.run(["monai", "segment", "--config", config_file])
        
        return mock_result
    
    def process_segmentation_results(
        self, 
        case_id: str,
        segmentation_results: Dict[str, Any]
    ) -> ImagingMetrics:
        """Segmentasyon sonuçlarını işler ve ImagingMetrics oluşturur"""
        
        logger.info(f"Segmentasyon sonuçları işleniyor: Case={case_id}")
        
        # Mock radyomik özellikler
        mock_radiomics = {
            "firstorder": {
                "mean": 2.45,
                "std": 0.89,
                "skewness": 0.12,
                "kurtosis": 0.34
            },
            "shape": {
                "volume": segmentation_results.get("total_volume", 0.0),
                "surface_area": 67.8,
                "sphericity": 0.78,
                "compactness": 0.65
            },
            "glcm": {
                "energy": 0.023,
                "contrast": 0.156,
                "correlation": 0.789,
                "homogeneity": 0.456
            }
        }
        
        # Mock SUV ölçümleri
        mock_suv = {
            "suvmax": 8.9,
            "suvmean": 5.2,
            "suvpeak": 7.8,
            "mtv": segmentation_results.get("total_volume", 0.0),
            "tlg": 235.0
        }
        
        # ImagingMetrics oluştur
        imaging_metrics = ImagingMetrics(
            case_id=case_id,
            segmentation_results=segmentation_results,
            radiomics_features=mock_radiomics,
            suv_measurements=mock_suv,
            percist_score=None,  # PERCIST sadece IMAGING yapıldıysa
            deauville_score=None,  # Deauville sadece IMAGING yapıldıysa
            processing_status=ProcessingStatus.COMPLETED
        )
        
        logger.info(f"ImagingMetrics oluşturuldu: Case={case_id}")
        return imaging_metrics

# ============================================================================
# MAIN INTEGRATION FUNCTION
# ============================================================================

def integrate_pico_with_monai(
    case_meta: CaseMeta,
    patient_packet: Dict[str, Any]
) -> Dict[str, Any]:
    """Ana entegrasyon fonksiyonu: PICO → MONAI"""
    
    logger.info(f"PICO-MONAI entegrasyonu başlatılıyor: Case={case_meta.case_id}")
    
    # Integration service oluştur
    integration_service = PICOMONAIIntegrationService()
    
    # Segmentasyon odak alanlarını belirle
    segmentation_strategy = integration_service.determine_segmentation_focus(
        icd_codes=patient_packet.get("icd_codes", []),
        clinical_goal=case_meta.clinical_goal
    )
    
    # MONAI konfigürasyonu oluştur
    monai_config = integration_service.create_monai_config(
        case_meta=case_meta,
        segmentation_strategy=segmentation_strategy
    )
    
    # Giriş verilerini doğrula
    validation_result = integration_service.validate_monai_input(
        case_meta=case_meta,
        segmentation_strategy=segmentation_strategy
    )
    
    if not validation_result["is_valid"]:
        logger.error(f"MONAI giriş validasyonu başarısız: {validation_result['errors']}")
        return {
            "success": False,
            "errors": validation_result["errors"],
            "case_id": case_meta.case_id
        }
    
    # MONAI segmentasyonunu başlat
    segmentation_result = integration_service.execute_monai_segmentation(
        monai_config=monai_config
    )
    
    # Sonuçları işle
    imaging_metrics = integration_service.process_segmentation_results(
        case_id=case_meta.case_id,
        segmentation_results=segmentation_result.get("segmentation_results", {})
    )
    
    # Entegrasyon sonucu
    integration_result = {
        "success": True,
        "case_id": case_meta.case_id,
        "segmentation_strategy": segmentation_strategy,
        "monai_config": monai_config,
        "validation_result": validation_result,
        "segmentation_result": segmentation_result,
        "imaging_metrics": imaging_metrics.dict(),
        "next_steps": [
            "PyRadiomics feature extraction",
            "SUV trend analysis",
            "PERCIST/Deauville scoring (if applicable)",
            "Decision packet creation"
        ]
    }
    
    logger.info(f"PICO-MONAI entegrasyonu tamamlandı: Case={case_meta.case_id}")
    return integration_result

# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "PICOMONAIIntegrationService",
    "integrate_pico_with_monai"
]
