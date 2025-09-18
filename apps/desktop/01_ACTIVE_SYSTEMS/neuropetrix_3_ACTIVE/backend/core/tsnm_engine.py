"""
TSNM (Tumor, Node, Metastasis) Raporlama Motoru
PERCIST standardına uygun ΔSUVpeak %30 kuralı entegrasyonu
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

class TSNMStage(Enum):
    """TSNM Evreleme"""
    T0 = "T0"  # Primer tümör yok
    T1 = "T1"  # Küçük tümör
    T2 = "T2"  # Orta tümör
    T3 = "T3"  # Büyük tümör
    T4 = "T4"  # Çok büyük tümör
    N0 = "N0"  # Lenf nodu yok
    N1 = "N1"  # Bölgesel lenf nodu
    N2 = "N2"  # Uzak lenf nodu
    M0 = "M0"  # Metastaz yok
    M1 = "M1"  # Metastaz var

class PERCISTResponse(Enum):
    """PERCIST Yanıt Kriterleri"""
    CR = "CR"  # Complete Response - Tam yanıt
    PR = "PR"  # Partial Response - Kısmi yanıt
    SD = "SD"  # Stable Disease - Stabil hastalık
    PD = "PD"  # Progressive Disease - İlerleyici hastalık
    NE = "NE"  # Not Evaluable - Değerlendirilemez

class TracerType(Enum):
    """PET Tracer Türleri"""
    FDG = "FDG"  # Fluorodeoxyglucose
    PSMA = "PSMA"  # Prostate-specific membrane antigen
    DOTATATE = "DOTATATE"  # Somatostatin receptor
    FAPI = "FAPI"  # Fibroblast activation protein inhibitor

@dataclass
class SUVMeasurement:
    """SUV Ölçümü"""
    value: float
    location: str
    measurement_type: str  # "peak", "max", "mean"
    timestamp: datetime
    confidence: float = 0.0

@dataclass
class TSNMFindings:
    """TSNM Bulguları"""
    primary_tumor: Optional[TSNMStage] = None
    lymph_nodes: Optional[TSNMStage] = None
    metastasis: Optional[TSNMStage] = None
    suv_measurements: List[SUVMeasurement] = None
    tracer_type: TracerType = TracerType.FDG
    
    def __post_init__(self):
        if self.suv_measurements is None:
            self.suv_measurements = []

@dataclass
class PERCISTAnalysis:
    """PERCIST Analizi"""
    baseline_suv: float
    followup_suv: float
    delta_suv_percent: float
    response: PERCISTResponse
    confidence: float
    analysis_date: datetime

class TSNMEngine:
    """TSNM Raporlama Motoru"""
    
    def __init__(self):
        self.templates_path = Path(__file__).parent / "templates"
        self.templates_path.mkdir(exist_ok=True)
        
        # Tracer-specific kurallar
        self.tracer_rules = {
            TracerType.FDG: {
                "normal_suv_max": 2.5,
                "suspicious_suv_max": 3.0,
                "malignant_suv_max": 4.0,
                "delta_threshold": 30.0  # %30 PERCIST kuralı
            },
            TracerType.PSMA: {
                "normal_suv_max": 3.0,
                "suspicious_suv_max": 4.0,
                "malignant_suv_max": 6.0,
                "delta_threshold": 25.0  # PSMA için %25
            },
            TracerType.DOTATATE: {
                "normal_suv_max": 2.0,
                "suspicious_suv_max": 3.0,
                "malignant_suv_max": 5.0,
                "delta_threshold": 30.0  # DOTATATE için %30
            }
        }
        
        # TSNM şablonları
        self.tsnm_templates = self._load_tsnm_templates()
        
        logger.info("TSNM Engine başlatıldı")

    def _load_tsnm_templates(self) -> Dict[str, Any]:
        """TSNM şablonlarını yükle"""
        templates = {
            "fdg": {
                "primary_tumor": {
                    "T0": "Primer tümör lezyonu saptanmamıştır.",
                    "T1": "Primer tümör lezyonu tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T2": "Primer tümör lezyonu orta boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T3": "Primer tümör lezyonu büyük boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T4": "Primer tümör lezyonu çok büyük boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}"
                },
                "lymph_nodes": {
                    "N0": "Bölgesel lenf nodu metastazı saptanmamıştır.",
                    "N1": "Bölgesel lenf nodu metastazı tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "N2": "Uzak lenf nodu metastazı tespit edilmiştir. SUVmax: {suv_max:.1f}"
                },
                "metastasis": {
                    "M0": "Uzak metastaz saptanmamıştır.",
                    "M1": "Uzak metastaz tespit edilmiştir. SUVmax: {suv_max:.1f}"
                }
            },
            "psma": {
                "primary_tumor": {
                    "T0": "Primer prostat tümör lezyonu saptanmamıştır.",
                    "T1": "Primer prostat tümör lezyonu tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T2": "Primer prostat tümör lezyonu orta boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T3": "Primer prostat tümör lezyonu büyük boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T4": "Primer prostat tümör lezyonu çok büyük boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}"
                },
                "lymph_nodes": {
                    "N0": "PSMA pozitif lenf nodu metastazı saptanmamıştır.",
                    "N1": "PSMA pozitif bölgesel lenf nodu metastazı tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "N2": "PSMA pozitif uzak lenf nodu metastazı tespit edilmiştir. SUVmax: {suv_max:.1f}"
                },
                "metastasis": {
                    "M0": "PSMA pozitif uzak metastaz saptanmamıştır.",
                    "M1": "PSMA pozitif uzak metastaz tespit edilmiştir. SUVmax: {suv_max:.1f}"
                }
            },
            "dotatate": {
                "primary_tumor": {
                    "T0": "Somatostatin reseptör pozitif primer tümör lezyonu saptanmamıştır.",
                    "T1": "Somatostatin reseptör pozitif primer tümör lezyonu tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T2": "Somatostatin reseptör pozitif primer tümör lezyonu orta boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T3": "Somatostatin reseptör pozitif primer tümör lezyonu büyük boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "T4": "Somatostatin reseptör pozitif primer tümör lezyonu çok büyük boyutta tespit edilmiştir. SUVmax: {suv_max:.1f}"
                },
                "lymph_nodes": {
                    "N0": "Somatostatin reseptör pozitif lenf nodu metastazı saptanmamıştır.",
                    "N1": "Somatostatin reseptör pozitif bölgesel lenf nodu metastazı tespit edilmiştir. SUVmax: {suv_max:.1f}",
                    "N2": "Somatostatin reseptör pozitif uzak lenf nodu metastazı tespit edilmiştir. SUVmax: {suv_max:.1f}"
                },
                "metastasis": {
                    "M0": "Somatostatin reseptör pozitif uzak metastaz saptanmamıştır.",
                    "M1": "Somatostatin reseptör pozitif uzak metastaz tespit edilmiştir. SUVmax: {suv_max:.1f}"
                }
            }
        }
        
        return templates

    def analyze_tsnm(self, findings: TSNMFindings) -> Dict[str, Any]:
        """TSNM analizi yap"""
        logger.info(f"TSNM analizi başlatıldı - Tracer: {findings.tracer_type.value}")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "tracer_type": findings.tracer_type.value,
            "tsnm_staging": {},
            "percist_analysis": None,
            "clinical_interpretation": "",
            "recommendations": []
        }
        
        # TSNM evreleme
        analysis["tsnm_staging"] = self._stage_tsnm(findings)
        
        # PERCIST analizi (eğer follow-up varsa)
        if len(findings.suv_measurements) >= 2:
            analysis["percist_analysis"] = self._analyze_percist(findings)
        
        # Klinik yorum
        analysis["clinical_interpretation"] = self._generate_clinical_interpretation(findings, analysis)
        
        # Öneriler
        analysis["recommendations"] = self._generate_recommendations(findings, analysis)
        
        logger.info("TSNM analizi tamamlandı")
        return analysis

    def _stage_tsnm(self, findings: TSNMFindings) -> Dict[str, Any]:
        """TSNM evreleme"""
        staging = {
            "T": findings.primary_tumor.value if findings.primary_tumor else "T0",
            "N": findings.lymph_nodes.value if findings.lymph_nodes else "N0", 
            "M": findings.metastasis.value if findings.metastasis else "M0",
            "stage_group": "",
            "description": {}
        }
        
        # Stage group belirleme
        staging["stage_group"] = self._determine_stage_group(staging["T"], staging["N"], staging["M"])
        
        # Açıklamalar
        tracer_key = findings.tracer_type.value.lower()
        templates = self.tsnm_templates.get(tracer_key, self.tsnm_templates["fdg"])
        
        # SUVmax değerlerini al
        suv_max = self._get_max_suv(findings.suv_measurements)
        
        # T açıklaması
        if staging["T"] in templates["primary_tumor"]:
            staging["description"]["T"] = templates["primary_tumor"][staging["T"]].format(suv_max=suv_max)
        
        # N açıklaması
        if staging["N"] in templates["lymph_nodes"]:
            staging["description"]["N"] = templates["lymph_nodes"][staging["N"]].format(suv_max=suv_max)
        
        # M açıklaması
        if staging["M"] in templates["metastasis"]:
            staging["description"]["M"] = templates["metastasis"][staging["M"]].format(suv_max=suv_max)
        
        return staging

    def _determine_stage_group(self, t: str, n: str, m: str) -> str:
        """Stage group belirleme (basitleştirilmiş)"""
        if m == "M1":
            return "Stage IV"
        elif n == "N2":
            return "Stage III"
        elif n == "N1":
            return "Stage II"
        elif t in ["T3", "T4"]:
            return "Stage II"
        elif t in ["T1", "T2"]:
            return "Stage I"
        else:
            return "Stage 0"

    def _get_max_suv(self, measurements: List[SUVMeasurement]) -> float:
        """Maksimum SUV değerini al"""
        if not measurements:
            return 0.0
        
        max_suv = max(measurements, key=lambda x: x.value)
        return max_suv.value

    def _analyze_percist(self, findings: TSNMFindings) -> Dict[str, Any]:
        """PERCIST analizi"""
        if len(findings.suv_measurements) < 2:
            return None
        
        # Baseline ve follow-up SUV değerlerini al
        baseline_suv = findings.suv_measurements[0].value
        followup_suv = findings.suv_measurements[-1].value
        
        # ΔSUV hesapla
        delta_suv_percent = ((followup_suv - baseline_suv) / baseline_suv) * 100
        
        # PERCIST yanıt belirleme
        tracer_rules = self.tracer_rules[findings.tracer_type]
        threshold = tracer_rules["delta_threshold"]
        
        if delta_suv_percent <= -threshold:
            response = PERCISTResponse.PR
        elif delta_suv_percent >= threshold:
            response = PERCISTResponse.PD
        else:
            response = PERCISTResponse.SD
        
        return {
            "baseline_suv": baseline_suv,
            "followup_suv": followup_suv,
            "delta_suv_percent": delta_suv_percent,
            "response": response.value,
            "threshold_used": threshold,
            "confidence": self._calculate_confidence(baseline_suv, followup_suv)
        }

    def _calculate_confidence(self, baseline: float, followup: float) -> float:
        """Güven skoru hesapla"""
        # Basit güven skoru hesaplama
        if baseline == 0:
            return 0.0
        
        ratio = followup / baseline
        if 0.5 <= ratio <= 2.0:
            return 0.9
        elif 0.3 <= ratio <= 3.0:
            return 0.7
        else:
            return 0.5

    def _generate_clinical_interpretation(self, findings: TSNMFindings, analysis: Dict[str, Any]) -> str:
        """Klinik yorum oluştur"""
        interpretation = []
        
        # Tracer-specific yorum
        tracer_type = findings.tracer_type.value
        if tracer_type == "FDG":
            interpretation.append("FDG-PET/CT incelemesinde:")
        elif tracer_type == "PSMA":
            interpretation.append("PSMA-PET/CT incelemesinde:")
        elif tracer_type == "DOTATATE":
            interpretation.append("DOTATATE-PET/CT incelemesinde:")
        
        # TSNM yorumu
        staging = analysis["tsnm_staging"]
        interpretation.append(f"TSNM evreleme: {staging['T']}{staging['N']}{staging['M']} ({staging['stage_group']})")
        
        # PERCIST yorumu
        if analysis["percist_analysis"]:
            percist = analysis["percist_analysis"]
            interpretation.append(
                f"PERCIST yanıt: {percist['response']} "
                f"(ΔSUV: {percist['delta_suv_percent']:.1f}%)"
            )
        
        return " ".join(interpretation)

    def _generate_recommendations(self, findings: TSNMFindings, analysis: Dict[str, Any]) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Tracer-specific öneriler
        tracer_type = findings.tracer_type.value
        if tracer_type == "PSMA":
            recommendations.append("Prostat kanseri takibi için PSMA-PET/CT önerilir")
        elif tracer_type == "DOTATATE":
            recommendations.append("Nöroendokrin tümör takibi için DOTATATE-PET/CT önerilir")
        
        # Stage-specific öneriler
        staging = analysis["tsnm_staging"]
        if staging["stage_group"] == "Stage IV":
            recommendations.append("Metastatik hastalık - sistemik tedavi önerilir")
        elif staging["stage_group"] in ["Stage II", "Stage III"]:
            recommendations.append("Lokal ileri hastalık - multimodal tedavi önerilir")
        
        # PERCIST önerileri
        if analysis["percist_analysis"]:
            percist = analysis["percist_analysis"]
            if percist["response"] == "PD":
                recommendations.append("Hastalık progresyonu - tedavi değişikliği önerilir")
            elif percist["response"] == "PR":
                recommendations.append("Tedavi yanıtı - mevcut tedaviye devam önerilir")
        
        return recommendations

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Rapor oluştur"""
        report = []
        report.append("=" * 60)
        report.append("TSNM RAPORU")
        report.append("=" * 60)
        report.append(f"Tarih: {analysis['timestamp']}")
        report.append(f"Tracer: {analysis['tracer_type']}")
        report.append("")
        
        # TSNM evreleme
        staging = analysis["tsnm_staging"]
        report.append("TSNM EVRELEME:")
        report.append(f"T: {staging['T']} - {staging['description'].get('T', '')}")
        report.append(f"N: {staging['N']} - {staging['description'].get('N', '')}")
        report.append(f"M: {staging['M']} - {staging['description'].get('M', '')}")
        report.append(f"Stage Group: {staging['stage_group']}")
        report.append("")
        
        # PERCIST analizi
        if analysis["percist_analysis"]:
            percist = analysis["percist_analysis"]
            report.append("PERCIST ANALİZİ:")
            report.append(f"Baseline SUV: {percist['baseline_suv']:.1f}")
            report.append(f"Follow-up SUV: {percist['followup_suv']:.1f}")
            report.append(f"ΔSUV: {percist['delta_suv_percent']:.1f}%")
            report.append(f"Yanıt: {percist['response']}")
            report.append(f"Güven: {percist['confidence']:.2f}")
            report.append("")
        
        # Klinik yorum
        report.append("KLİNİK YORUM:")
        report.append(analysis["clinical_interpretation"])
        report.append("")
        
        # Öneriler
        if analysis["recommendations"]:
            report.append("ÖNERİLER:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                report.append(f"{i}. {rec}")
        
        return "\n".join(report)

# Kullanım örneği
if __name__ == "__main__":
    # Test verisi
    findings = TSNMFindings(
        primary_tumor=TSNMStage.T2,
        lymph_nodes=TSNMStage.N1,
        metastasis=TSNMStage.M0,
        tracer_type=TracerType.FDG,
        suv_measurements=[
            SUVMeasurement(4.5, "Primer tümör", "max", datetime.now()),
            SUVMeasurement(3.2, "Lenf nodu", "max", datetime.now()),
            SUVMeasurement(2.8, "Primer tümör", "max", datetime.now())  # Follow-up
        ]
    )
    
    # Engine'i başlat
    engine = TSNMEngine()
    
    # Analiz yap
    analysis = engine.analyze_tsnm(findings)
    
    # Rapor oluştur
    report = engine.generate_report(analysis)
    print(report)
