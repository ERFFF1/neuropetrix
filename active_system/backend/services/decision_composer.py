"""
NeuroPETrix v2.0 - Decision Composer Service
clinical_goal, evidence_packet ve imaging_metrics verilerini alarak AI_CONCLUSION üretir
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from schemas.integration_packets import (
    ClinicalGoal, EvidencePacket, ImagingMetrics, 
    DecisionPacket, ProcessingStatus
)

# Gemini AI Studio entegrasyonu
try:
    from .gemini_service import gemini_service
    GEMINI_AVAILABLE = True
    logger.info("✅ Gemini AI Studio entegrasyonu başarılı")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ Gemini AI Studio entegrasyonu bulunamadı, fallback mode kullanılıyor")

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DECISION COMPOSER SERVICE
# ============================================================================

class DecisionComposerService:
    """AI karar ve öneri üretimi için ana servis"""
    
    def __init__(self):
        self.clinical_goal_templates = {
            ClinicalGoal.DIAGNOSIS: {
                "high_confidence": "PET-CT findings confirm {diagnosis} with high confidence. {action} is recommended.",
                "moderate_confidence": "PET-CT findings suggest {diagnosis} with moderate confidence. {action} is recommended for confirmation.",
                "low_confidence": "PET-CT findings are inconclusive for {diagnosis}. {action} is recommended for further evaluation."
            },
            ClinicalGoal.TREATMENT: {
                "high_confidence": "PET-CT findings support {treatment} approach with high confidence. {action} is recommended.",
                "moderate_confidence": "PET-CT findings suggest {treatment} approach with moderate confidence. {action} is recommended.",
                "low_confidence": "PET-CT findings provide limited support for {treatment}. {action} is recommended for reassessment."
            },
            ClinicalGoal.PROGNOSIS: {
                "high_confidence": "PET-CT findings indicate {prognosis} prognosis with high confidence. {action} is recommended.",
                "moderate_confidence": "PET-CT findings suggest {prognosis} prognosis with moderate confidence. {action} is recommended.",
                "low_confidence": "PET-CT findings provide limited prognostic information. {action} is recommended for monitoring."
            },
            ClinicalGoal.FOLLOW_UP: {
                "high_confidence": "PET-CT findings show {response} response to treatment with high confidence. {action} is recommended.",
                "moderate_confidence": "PET-CT findings suggest {response} response to treatment with moderate confidence. {action} is recommended.",
                "low_confidence": "PET-CT findings provide limited information about treatment response. {action} is recommended."
            }
        }
        
        self.action_recommendations = {
            ClinicalGoal.DIAGNOSIS: {
                "lung": "Proceed with tissue biopsy for definitive diagnosis",
                "liver": "Consider liver biopsy or additional imaging",
                "brain": "Refer to neurosurgery for tissue sampling",
                "breast": "Proceed with breast biopsy",
                "prostate": "Consider prostate biopsy"
            },
            ClinicalGoal.TREATMENT: {
                "lung": "Proceed with treatment planning based on staging",
                "liver": "Consider surgical resection or systemic therapy",
                "brain": "Refer to neuro-oncology for treatment planning",
                "breast": "Proceed with surgery or neoadjuvant therapy",
                "prostate": "Consider surgery, radiation, or systemic therapy"
            },
            ClinicalGoal.PROGNOSIS: {
                "lung": "Monitor closely with regular follow-up imaging",
                "liver": "Assess liver function and consider surveillance",
                "brain": "Monitor neurological status and imaging",
                "breast": "Regular follow-up with mammography and clinical exam",
                "prostate": "Monitor PSA levels and consider imaging follow-up"
            },
            ClinicalGoal.FOLLOW_UP: {
                "lung": "Continue current treatment and monitor response",
                "liver": "Assess treatment response and adjust if needed",
                "brain": "Monitor treatment response and side effects",
                "breast": "Continue adjuvant therapy and monitor",
                "prostate": "Monitor treatment response and PSA levels"
            }
        }
        
        self.risk_benefit_templates = {
            "high_confidence": {
                "benefits": "High diagnostic accuracy, comprehensive staging, treatment guidance",
                "risks": "Radiation exposure, potential false positive findings"
            },
            "moderate_confidence": {
                "benefits": "Good diagnostic accuracy, staging information, treatment planning",
                "risks": "Radiation exposure, moderate false positive rate, may need additional tests"
            },
            "low_confidence": {
                "benefits": "Basic imaging information, initial assessment",
                "risks": "Radiation exposure, high false positive rate, additional tests required"
            }
        }
    
    def compose_decision(
        self,
        case_id: str,
        clinical_goal: ClinicalGoal,
        evidence_packet: EvidencePacket,
        imaging_metrics: ImagingMetrics,
        patient_packet: Dict[str, Any]
    ) -> DecisionPacket:
        """Ana karar oluşturma fonksiyonu"""
        
        logger.info(f"Karar oluşturuluyor: Case={case_id}, Goal={clinical_goal}")
        
        # Kanıt özeti oluştur
        evidence_summary = self._create_evidence_summary(evidence_packet)
        
        # Görüntüleme bulguları oluştur
        imaging_findings = self._create_imaging_findings(imaging_metrics)
        
        # AI sonucu oluştur - Gemini AI Studio entegrasyonu ile
        ai_conclusion = self._create_ai_conclusion_with_gemini(
            clinical_goal=clinical_goal,
            evidence_packet=evidence_packet,
            imaging_metrics=imaging_metrics,
            patient_packet=patient_packet
        )
        
        # Öneriler oluştur
        recommendations = self._create_recommendations(
            clinical_goal=clinical_goal,
            evidence_packet=evidence_packet,
            imaging_metrics=imaging_metrics,
            patient_packet=patient_packet
        )
        
        # Risk-fayda analizi
        risk_benefit = self._create_risk_benefit_analysis(
            evidence_packet=evidence_packet,
            imaging_metrics=imaging_metrics
        )
        
        # Kontrendikasyonlar
        contraindications = self._identify_contraindications(
            patient_packet=patient_packet,
            imaging_metrics=imaging_metrics
        )
        
        # Uygulanabilirlik skoru
        applicability_score = self._calculate_applicability_score(
            evidence_packet=evidence_packet,
            imaging_metrics=imaging_metrics,
            patient_packet=patient_packet
        )
        
        # DecisionPacket oluştur
        decision_packet = DecisionPacket(
            case_id=case_id,
            clinical_goal=clinical_goal,
            evidence_summary=evidence_summary,
            imaging_findings=imaging_findings,
            ai_conclusion=ai_conclusion,
            recommendations=recommendations,
            risk_benefit=risk_benefit,
            contraindications=contraindications,
            applicability_score=applicability_score
        )
        
        logger.info(f"Karar oluşturuldu: Case={case_id}")
        return decision_packet
    
    def _create_evidence_summary(self, evidence_packet: EvidencePacket) -> str:
        """Kanıt özeti oluşturur"""
        
        grade = evidence_packet.grade_assessment.get("overall_grade", "Unknown")
        evidence_quality = evidence_packet.grade_assessment.get("quality", "Unknown")
        
        summary = f"PET-CT shows {evidence_packet.evidence_summary} "
        summary += f"with {evidence_quality.lower()} quality evidence (Grade {grade})."
        
        return summary
    
    def _create_imaging_findings(self, imaging_metrics: ImagingMetrics) -> str:
        """Görüntüleme bulguları oluşturur"""
        
        lesion_count = imaging_metrics.segmentation_results.get("lesion_count", 0)
        suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
        total_volume = imaging_metrics.segmentation_results.get("total_volume", 0.0)
        
        findings = f"{lesion_count} lesion(s) detected with SUVmax {suvmax:.1f}"
        
        if total_volume > 0:
            findings += f", total volume {total_volume:.1f}cc"
        
        # PERCIST skoru varsa ekle
        if imaging_metrics.percist_score:
            findings += f". PERCIST score: {imaging_metrics.percist_score}"
        
        # Deauville skoru varsa ekle
        if imaging_metrics.deauville_score:
            findings += f". Deauville score: {imaging_metrics.deauville_score}"
        
        return findings
    
    def _format_gemini_conclusion(self, gemini_result: Dict[str, Any]) -> str:
        """Gemini AI sonucunu format'lar"""
        try:
            ai_conclusion = gemini_result.get("ai_conclusion", "Unknown")
            rationale_keys = gemini_result.get("rationale_keys", [])
            optional = gemini_result.get("optional", {})
            
            # Ana sonuç
            formatted = f"AI Conclusion: {ai_conclusion}\n"
            
            # Rationale
            if rationale_keys:
                formatted += f"Rationale: {', '.join(rationale_keys)}\n"
            
            # PERCIST
            if optional.get("percist"):
                formatted += f"PERCIST: {optional['percist']}\n"
            
            # Deauville
            if optional.get("deauville"):
                formatted += f"Deauville Score: {optional['deauville']}\n"
            
            # QC Flags
            if optional.get("qc_flags"):
                formatted += f"QC Warnings: {', '.join(optional['qc_flags'])}\n"
            
            # GRADE
            if optional.get("grade_summary"):
                formatted += f"Evidence Quality: {optional['grade_summary']}\n"
            
            return formatted.strip()
            
        except Exception as e:
            logger.error(f"Gemini conclusion formatting failed: {e}")
            return "AI Conclusion: Error in formatting"
    
    def _create_ai_conclusion_with_gemini(
        self,
        clinical_goal: ClinicalGoal,
        evidence_packet: EvidencePacket,
        imaging_metrics: ImagingMetrics,
        patient_packet: Dict[str, Any]
    ) -> str:
        
        # Gemini AI Studio entegrasyonu varsa kullan
        if GEMINI_AVAILABLE:
            try:
                # Clinical goal'u string'e çevir
                clinical_goal_str = clinical_goal.value if hasattr(clinical_goal, 'value') else str(clinical_goal)
                
                # Imaging metrics'i dict'e çevir
                imaging_dict = {
                    "suvmax": imaging_metrics.suv_measurements.get("suvmax", 0.0),
                    "mtv": imaging_metrics.segmentation_results.get("total_volume", 0.0),
                    "tlg": imaging_metrics.suv_measurements.get("suvmax", 0.0) * imaging_metrics.segmentation_results.get("total_volume", 0.0),
                    "percist": imaging_metrics.percist_score,
                    "deauville": imaging_metrics.deauville_score if hasattr(imaging_metrics, 'deauville_score') else None
                }
                
                # Evidence summary
                evidence_summary = evidence_packet.evidence_summary if hasattr(evidence_packet, 'evidence_summary') else "Evidence available"
                
                # Gemini AI conclusion üret
                gemini_result = gemini_service.generate_ai_conclusion(
                    clinical_goal=clinical_goal_str,
                    imaging_available=True,
                    imaging_metrics=imaging_dict,
                    qc_flags=imaging_metrics.qc_flags if hasattr(imaging_metrics, 'qc_flags') else [],
                    evidence_summary=evidence_summary
                )
                
                logger.info(f"Gemini AI conclusion generated: {gemini_result.get('ai_conclusion', 'Unknown')}")
                
                # Gemini sonucunu format'la
                ai_conclusion = self._format_gemini_conclusion(gemini_result)
                return ai_conclusion
                
            except Exception as e:
                logger.warning(f"Gemini AI conclusion failed, fallback kullanılıyor: {e}")
        
        # Fallback: Orijinal AI conclusion
        # Fallback: Orijinal AI conclusion
        return self._create_ai_conclusion(
            clinical_goal=clinical_goal,
            evidence_packet=evidence_packet,
            imaging_metrics=imaging_metrics,
            patient_packet=patient_packet
        )
    
    def _create_ai_conclusion(
        self,
        clinical_goal: ClinicalGoal,
        evidence_packet: EvidencePacket,
        imaging_metrics: ImagingMetrics,
        patient_packet: Dict[str, Any]
    ) -> str:
        """AI sonucu oluşturur - kısa ve eylem odaklı"""
        
        # ICD kodlarından organ tespiti
        icd_codes = patient_packet.get("icd_codes", [])
        target_organ = self._identify_target_organ(icd_codes)
        
        # Kanıt kalitesi
        grade = evidence_packet.grade_assessment.get("overall_grade", "Unknown")
        confidence_level = self._determine_confidence_level(grade)
        
        # Template seçimi
        template = self.clinical_goal_templates[clinical_goal][confidence_level]
        
        # Placeholder'ları doldur
        if clinical_goal == ClinicalGoal.DIAGNOSIS:
            diagnosis = self._get_diagnosis_from_icd(icd_codes)
            action = self.action_recommendations[clinical_goal].get(target_organ, "Proceed with appropriate diagnostic workup")
            conclusion = template.format(diagnosis=diagnosis, action=action)
        
        elif clinical_goal == ClinicalGoal.TREATMENT:
            treatment = self._get_treatment_approach(imaging_metrics, evidence_packet)
            action = self.action_recommendations[clinical_goal].get(target_organ, "Proceed with appropriate treatment planning")
            conclusion = template.format(treatment=treatment, action=action)
        
        elif clinical_goal == ClinicalGoal.PROGNOSIS:
            prognosis = self._assess_prognosis(imaging_metrics, evidence_packet)
            action = self.action_recommendations[clinical_goal].get(target_organ, "Monitor closely with appropriate follow-up")
            conclusion = template.format(prognosis=prognosis, action=action)
        
        elif clinical_goal == ClinicalGoal.FOLLOW_UP:
            response = self._assess_treatment_response(imaging_metrics)
            action = self.action_recommendations[clinical_goal].get(target_organ, "Continue current treatment and monitor")
            conclusion = template.format(response=response, action=action)
        
        else:
            conclusion = "PET-CT findings require clinical correlation and appropriate follow-up."
        
        return conclusion
    
    def _create_recommendations(
        self,
        clinical_goal: ClinicalGoal,
        evidence_packet: EvidencePacket,
        imaging_metrics: ImagingMetrics,
        patient_packet: Dict[str, Any]
    ) -> List[str]:
        """Detaylı öneriler oluşturur"""
        
        recommendations = []
        
        # Ana öneri
        icd_codes = patient_packet.get("icd_codes", [])
        target_organ = self._identify_target_organ(icd_codes)
        
        if clinical_goal == ClinicalGoal.DIAGNOSIS:
            recommendations.append(f"Proceed with {target_organ} biopsy for definitive diagnosis")
            recommendations.append("Consider additional staging imaging if clinically indicated")
            recommendations.append("Refer to appropriate specialist for further evaluation")
        
        elif clinical_goal == ClinicalGoal.TREATMENT:
            recommendations.append(f"Proceed with {target_organ} treatment planning based on staging")
            recommendations.append("Consider multidisciplinary tumor board discussion")
            recommendations.append("Implement appropriate supportive care measures")
        
        elif clinical_goal == ClinicalGoal.PROGNOSIS:
            recommendations.append(f"Monitor {target_organ} status with regular follow-up imaging")
            recommendations.append("Assess response to current treatment")
            recommendations.append("Consider prognostic biomarker testing if available")
        
        elif clinical_goal == ClinicalGoal.FOLLOW_UP:
            recommendations.append(f"Continue current {target_organ} treatment and monitor response")
            recommendations.append("Schedule regular follow-up imaging")
            recommendations.append("Assess for treatment-related side effects")
        
        # Kanıta dayalı öneriler
        if evidence_packet.recommendations:
            recommendations.extend(evidence_packet.recommendations)
        
        # SUV trend önerileri
        if imaging_metrics.suv_measurements:
            suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
            if suvmax > 10.0:
                recommendations.append("High SUVmax suggests aggressive disease - consider immediate intervention")
            elif suvmax > 5.0:
                recommendations.append("Moderate SUVmax - monitor closely and consider treatment adjustment")
        
        return recommendations
    
    def _create_risk_benefit_analysis(
        self,
        evidence_packet: EvidencePacket,
        imaging_metrics: ImagingMetrics
    ) -> Dict[str, str]:
        """Risk-fayda analizi oluşturur"""
        
        grade = evidence_packet.grade_assessment.get("overall_grade", "Unknown")
        confidence_level = self._determine_confidence_level(grade)
        
        base_risk_benefit = self.risk_benefit_templates[confidence_level]
        
        # SUV bazlı ek riskler
        additional_risks = []
        if imaging_metrics.suv_measurements:
            suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
            if suvmax > 15.0:
                additional_risks.append("Very high SUVmax may indicate aggressive disease requiring immediate attention")
            elif suvmax > 10.0:
                additional_risks.append("High SUVmax suggests need for prompt intervention")
        
        # Ek faydalar
        additional_benefits = []
        if imaging_metrics.percist_score:
            additional_benefits.append(f"PERCIST scoring available for treatment response assessment")
        if imaging_metrics.deauville_score:
            additional_benefits.append(f"Deauville scoring available for lymphoma assessment")
        
        # Risk-fayda analizi
        risk_benefit = {
            "benefits": f"{base_risk_benefit['benefits']}. {' '.join(additional_benefits)}",
            "risks": f"{base_risk_benefit['risks']}. {' '.join(additional_risks)}"
        }
        
        return risk_benefit
    
    def _identify_contraindications(
        self,
        patient_packet: Dict[str, Any],
        imaging_metrics: ImagingMetrics
    ) -> List[str]:
        """Kontrendikasyonları belirler"""
        
        contraindications = []
        
        # Hasta bazlı kontrendikasyonlar
        clinical_data = patient_packet.get("clinical", {})
        allergies = clinical_data.get("allergies", [])
        
        if "iodine" in [allergy.lower() for allergy in allergies]:
            contraindications.append("Iodine allergy - consider alternative contrast agents")
        
        if "gadolinium" in [allergy.lower() for allergy in allergies]:
            contraindications.append("Gadolinium allergy - consider alternative contrast agents")
        
        # Görüntüleme bazlı kontrendikasyonlar
        if imaging_metrics.segmentation_results.get("segmentation_quality") == "poor":
            contraindications.append("Poor image quality - consider repeat imaging")
        
        if imaging_metrics.suv_measurements.get("suvmax", 0.0) < 1.0:
            contraindications.append("Very low SUV values - consider technical factors or repeat study")
        
        return contraindications
    
    def _calculate_applicability_score(
        self,
        evidence_packet: EvidencePacket,
        imaging_metrics: ImagingMetrics,
        patient_packet: Dict[str, Any]
    ) -> float:
        """Uygulanabilirlik skorunu hesaplar (0-1)"""
        
        score = 0.0
        
        # Kanıt kalitesi (0.4 puan)
        grade = evidence_packet.grade_assessment.get("overall_grade", "Unknown")
        grade_scores = {"A": 0.4, "B": 0.3, "C": 0.2, "D": 0.1}
        score += grade_scores.get(grade, 0.1)
        
        # Görüntü kalitesi (0.3 puan)
        quality = imaging_metrics.segmentation_results.get("segmentation_quality", "unknown")
        quality_scores = {"excellent": 0.3, "good": 0.25, "fair": 0.2, "poor": 0.1}
        score += quality_scores.get(quality, 0.15)
        
        # SUV değerleri (0.2 puan)
        suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
        if 2.0 <= suvmax <= 15.0:
            score += 0.2
        elif 1.0 <= suvmax < 2.0 or 15.0 < suvmax <= 20.0:
            score += 0.15
        else:
            score += 0.1
        
        # Hasta verisi tamlığı (0.1 puan)
        required_fields = ["demographics", "laboratory", "clinical", "icd_codes"]
        completeness = sum(1 for field in required_fields if patient_packet.get(field)) / len(required_fields)
        score += completeness * 0.1
        
        return min(score, 1.0)
    
    def _identify_target_organ(self, icd_codes: List[str]) -> str:
        """ICD kodlarından hedef organı belirler"""
        
        organ_mapping = {
            "C34": "lung",
            "C22": "liver", 
            "C71": "brain",
            "C50": "breast",
            "C61": "prostate",
            "C18": "colon",
            "C16": "stomach",
            "C25": "pancreas",
            "C67": "bladder",
            "C73": "thyroid"
        }
        
        for icd_code in icd_codes:
            organ_prefix = icd_code[:3]
            if organ_prefix in organ_mapping:
                return organ_mapping[organ_prefix]
        
        return "primary_organ"
    
    def _get_diagnosis_from_icd(self, icd_codes: List[str]) -> str:
        """ICD kodlarından tanıyı belirler"""
        
        diagnosis_mapping = {
            "C34": "lung cancer",
            "C22": "liver cancer",
            "C71": "brain cancer", 
            "C50": "breast cancer",
            "C61": "prostate cancer",
            "C18": "colon cancer",
            "C16": "stomach cancer",
            "C25": "pancreatic cancer",
            "C67": "bladder cancer",
            "C73": "thyroid cancer"
        }
        
        for icd_code in icd_codes:
            organ_prefix = icd_code[:3]
            if organ_prefix in diagnosis_mapping:
                return diagnosis_mapping[organ_prefix]
        
        return "suspected malignancy"
    
    def _get_treatment_approach(
        self,
        imaging_metrics: ImagingMetrics,
        evidence_packet: EvidencePacket
    ) -> str:
        """Görüntüleme bulgularına göre tedavi yaklaşımını belirler"""
        
        suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
        lesion_count = imaging_metrics.segmentation_results.get("lesion_count", 0)
        
        if suvmax > 10.0 and lesion_count > 2:
            return "aggressive systemic therapy"
        elif suvmax > 5.0:
            return "standard therapy with close monitoring"
        else:
            return "conservative therapy with surveillance"
    
    def _assess_prognosis(
        self,
        imaging_metrics: ImagingMetrics,
        evidence_packet: EvidencePacket
    ) -> str:
        """Görüntüleme bulgularına göre prognozu değerlendirir"""
        
        suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
        total_volume = imaging_metrics.segmentation_results.get("total_volume", 0.0)
        
        if suvmax > 10.0 and total_volume > 50.0:
            return "poor prognosis"
        elif suvmax > 5.0 or total_volume > 20.0:
            return "moderate prognosis"
        else:
            return "favorable prognosis"
    
    def _assess_treatment_response(self, imaging_metrics: ImagingMetrics) -> str:
        """Tedavi yanıtını değerlendirir"""
        
        if imaging_metrics.percist_score:
            percist_mapping = {
                "CR": "complete response",
                "PR": "partial response", 
                "SD": "stable disease",
                "PD": "progressive disease"
            }
            return percist_mapping.get(imaging_metrics.percist_score, "unknown response")
        
        # SUV değişimine göre
        suvmax = imaging_metrics.suv_measurements.get("suvmax", 0.0)
        if suvmax < 2.0:
            return "good response"
        elif suvmax < 5.0:
            return "moderate response"
        else:
            return "poor response"
    
    def _determine_confidence_level(self, grade: str) -> str:
        """GRADE skoruna göre güven seviyesini belirler"""
        
        if grade in ["A", "B"]:
            return "high_confidence"
        elif grade == "C":
            return "moderate_confidence"
        else:
            return "low_confidence"

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def compose_clinical_decision(
    case_id: str,
    clinical_goal: ClinicalGoal,
    evidence_packet: EvidencePacket,
    imaging_metrics: ImagingMetrics,
    patient_packet: Dict[str, Any]
) -> DecisionPacket:
    """Ana klinik karar oluşturma fonksiyonu"""
    
    logger.info(f"Klinik karar oluşturuluyor: Case={case_id}")
    
    composer = DecisionComposerService()
    decision = composer.compose_decision(
        case_id=case_id,
        clinical_goal=clinical_goal,
        evidence_packet=evidence_packet,
        imaging_metrics=imaging_metrics,
        patient_packet=patient_packet
    )
    
    logger.info(f"Klinik karar oluşturuldu: Case={case_id}")
    return decision

# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "DecisionComposerService",
    "compose_clinical_decision"
]
