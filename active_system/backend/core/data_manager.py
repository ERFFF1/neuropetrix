"""
Data Manager - Otomatik Anonimleştirme & FHIR Integration
Nash ID eşleştirme, SUV trend logları, FHIR DiagnosticReport
"""

import logging
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re

logger = logging.getLogger(__name__)

@dataclass
class PatientData:
    """Hasta Verisi"""
    patient_id: str
    name: str
    surname: str
    birth_date: str
    gender: str
    mrn: str  # Medical Record Number
    study_date: datetime
    study_type: str
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnonymizedPatient:
    """Anonimleştirilmiş Hasta"""
    nash_id: str  # Nash Hash ID
    age_group: str  # 0-18, 19-65, 65+
    gender: str
    study_date: datetime
    study_type: str
    anonymized_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SUVTrendLog:
    """SUV Trend Log"""
    log_id: str
    nash_id: str
    measurement_date: datetime
    suv_max: float
    suv_peak: float
    suv_mean: float
    location: str
    tracer_type: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FHIRDiagnosticReport:
    """FHIR DiagnosticReport"""
    resource_id: str
    nash_id: str
    report_date: datetime
    status: str  # final, preliminary, amended, corrected, appended, cancelled
    category: str
    code: str
    subject: Dict[str, Any]
    performer: Dict[str, Any]
    result: List[Dict[str, Any]]
    conclusion: str
    fhir_data: Dict[str, Any] = field(default_factory=dict)

class DataManager:
    """Veri Yönetim Motoru"""
    
    def __init__(self):
        self.anonymized_patients: Dict[str, AnonymizedPatient] = {}
        self.suv_trend_logs: Dict[str, List[SUVTrendLog]] = {}
        self.fhir_reports: Dict[str, FHIRDiagnosticReport] = {}
        self.nash_mapping: Dict[str, str] = {}  # MRN -> Nash ID mapping
        
        # Anonimleştirme kuralları
        self.anonymization_rules = {
            "name": "***",
            "surname": "***",
            "mrn": lambda x: f"MRN_{hashlib.md5(x.encode()).hexdigest()[:8]}",
            "phone": "***",
            "address": "***",
            "email": "***"
        }
        
        logger.info("Data Manager başlatıldı")

    def anonymize_patient_data(self, patient_data: PatientData) -> AnonymizedPatient:
        """Hasta verisini anonimleştir"""
        logger.info(f"Hasta verisi anonimleştiriliyor: {patient_data.patient_id}")
        
        # Nash ID oluştur (deterministic hash)
        nash_input = f"{patient_data.mrn}_{patient_data.birth_date}_{patient_data.gender}"
        nash_id = hashlib.sha256(nash_input.encode()).hexdigest()[:16]
        
        # Yaş grubu hesapla
        birth_year = int(patient_data.birth_date.split('-')[0])
        current_year = datetime.now().year
        age = current_year - birth_year
        
        if age <= 18:
            age_group = "0-18"
        elif age <= 65:
            age_group = "19-65"
        else:
            age_group = "65+"
        
        # Anonimleştirilmiş veri oluştur
        anonymized_data = {
            "original_patient_id": patient_data.patient_id,
            "anonymization_date": datetime.now().isoformat(),
            "study_details": {
                "study_type": patient_data.study_type,
                "study_date": patient_data.study_date.isoformat(),
                "age_group": age_group,
                "gender": patient_data.gender
            }
        }
        
        # Nash ID mapping'i kaydet
        self.nash_mapping[patient_data.mrn] = nash_id
        
        # Anonimleştirilmiş hasta oluştur
        anonymized_patient = AnonymizedPatient(
            nash_id=nash_id,
            age_group=age_group,
            gender=patient_data.gender,
            study_date=patient_data.study_date,
            study_type=patient_data.study_type,
            anonymized_data=anonymized_data
        )
        
        # Kaydet
        self.anonymized_patients[nash_id] = anonymized_patient
        
        logger.info(f"Hasta anonimleştirildi - Nash ID: {nash_id}")
        return anonymized_patient

    def load_old_report(self, report_data: Dict[str, Any]) -> Tuple[AnonymizedPatient, Dict[str, Any]]:
        """Eski raporu yükle ve otomatik anonimleştir"""
        logger.info("Eski rapor yükleniyor ve anonimleştiriliyor")
        
        # Hasta verisini çıkar
        patient_data = PatientData(
            patient_id=report_data.get("patient_id", ""),
            name=report_data.get("patient_name", ""),
            surname=report_data.get("patient_surname", ""),
            birth_date=report_data.get("birth_date", "1900-01-01"),
            gender=report_data.get("gender", "unknown"),
            mrn=report_data.get("mrn", ""),
            study_date=datetime.fromisoformat(report_data.get("study_date", datetime.now().isoformat())),
            study_type=report_data.get("study_type", "PET/CT"),
            raw_data=report_data
        )
        
        # Anonimleştir
        anonymized_patient = self.anonymize_patient_data(patient_data)
        
        # Rapor verisini anonimleştir
        anonymized_report = self._anonymize_report_data(report_data, anonymized_patient.nash_id)
        
        return anonymized_patient, anonymized_report

    def _anonymize_report_data(self, report_data: Dict[str, Any], nash_id: str) -> Dict[str, Any]:
        """Rapor verisini anonimleştir"""
        anonymized_report = report_data.copy()
        
        # Kişisel bilgileri anonimleştir
        for field, rule in self.anonymization_rules.items():
            if field in anonymized_report:
                if callable(rule):
                    anonymized_report[field] = rule(anonymized_report[field])
                else:
                    anonymized_report[field] = rule
        
        # Nash ID ekle
        anonymized_report["nash_id"] = nash_id
        anonymized_report["anonymization_date"] = datetime.now().isoformat()
        
        return anonymized_report

    def add_suv_trend_log(self, nash_id: str, suv_data: Dict[str, Any]) -> SUVTrendLog:
        """SUV trend log ekle"""
        log_id = str(uuid.uuid4())
        
        suv_log = SUVTrendLog(
            log_id=log_id,
            nash_id=nash_id,
            measurement_date=datetime.fromisoformat(suv_data.get("measurement_date", datetime.now().isoformat())),
            suv_max=suv_data.get("suv_max", 0.0),
            suv_peak=suv_data.get("suv_peak", 0.0),
            suv_mean=suv_data.get("suv_mean", 0.0),
            location=suv_data.get("location", ""),
            tracer_type=suv_data.get("tracer_type", "FDG"),
            confidence=suv_data.get("confidence", 0.0),
            metadata=suv_data.get("metadata", {})
        )
        
        # Nash ID'ye göre grupla
        if nash_id not in self.suv_trend_logs:
            self.suv_trend_logs[nash_id] = []
        
        self.suv_trend_logs[nash_id].append(suv_log)
        
        # Tarihe göre sırala
        self.suv_trend_logs[nash_id].sort(key=lambda x: x.measurement_date)
        
        logger.info(f"SUV trend log eklendi: {log_id} - Nash ID: {nash_id}")
        return suv_log

    def get_suv_trend_data(self, nash_id: str) -> Dict[str, Any]:
        """SUV trend verilerini getir"""
        if nash_id not in self.suv_trend_logs:
            return {"nash_id": nash_id, "trends": [], "summary": {}}
        
        trends = self.suv_trend_logs[nash_id]
        
        # Trend analizi
        if len(trends) < 2:
            return {
                "nash_id": nash_id,
                "trends": [self._suv_log_to_dict(log) for log in trends],
                "summary": {"status": "insufficient_data", "message": "En az 2 ölçüm gerekli"}
            }
        
        # Trend hesapla
        first_measurement = trends[0]
        last_measurement = trends[-1]
        
        delta_suv_max = last_measurement.suv_max - first_measurement.suv_max
        delta_suv_percent = (delta_suv_max / first_measurement.suv_max) * 100 if first_measurement.suv_max > 0 else 0
        
        # Trend yönü
        if delta_suv_percent > 10:
            trend_direction = "increasing"
        elif delta_suv_percent < -10:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        summary = {
            "total_measurements": len(trends),
            "first_measurement": first_measurement.measurement_date.isoformat(),
            "last_measurement": last_measurement.measurement_date.isoformat(),
            "delta_suv_max": delta_suv_max,
            "delta_suv_percent": delta_suv_percent,
            "trend_direction": trend_direction,
            "average_suv_max": sum(log.suv_max for log in trends) / len(trends),
            "max_suv_max": max(log.suv_max for log in trends),
            "min_suv_max": min(log.suv_max for log in trends)
        }
        
        return {
            "nash_id": nash_id,
            "trends": [self._suv_log_to_dict(log) for log in trends],
            "summary": summary
        }

    def _suv_log_to_dict(self, log: SUVTrendLog) -> Dict[str, Any]:
        """SUV log'u dictionary'ye çevir"""
        return {
            "log_id": log.log_id,
            "measurement_date": log.measurement_date.isoformat(),
            "suv_max": log.suv_max,
            "suv_peak": log.suv_peak,
            "suv_mean": log.suv_mean,
            "location": log.location,
            "tracer_type": log.tracer_type,
            "confidence": log.confidence,
            "metadata": log.metadata
        }

    def create_fhir_diagnostic_report(self, nash_id: str, report_data: Dict[str, Any]) -> FHIRDiagnosticReport:
        """FHIR DiagnosticReport oluştur"""
        resource_id = str(uuid.uuid4())
        
        # FHIR DiagnosticReport oluştur
        fhir_report = {
            "resourceType": "DiagnosticReport",
            "id": resource_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "11502-2",
                            "display": "Laboratory report"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11502-2",
                        "display": "Laboratory report"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{nash_id}",
                "display": f"Patient {nash_id}"
            },
            "performer": [
                {
                    "reference": "Practitioner/neuropetrix-ai",
                    "display": "NeuroPETRIX AI System"
                }
            ],
            "result": report_data.get("findings", []),
            "conclusion": report_data.get("conclusion", ""),
            "issued": datetime.now().isoformat(),
            "effectiveDateTime": report_data.get("study_date", datetime.now().isoformat())
        }
        
        # FHIR DiagnosticReport oluştur
        diagnostic_report = FHIRDiagnosticReport(
            resource_id=resource_id,
            nash_id=nash_id,
            report_date=datetime.now(),
            status="final",
            category="laboratory",
            code="11502-2",
            subject={"reference": f"Patient/{nash_id}"},
            performer={"reference": "Practitioner/neuropetrix-ai"},
            result=report_data.get("findings", []),
            conclusion=report_data.get("conclusion", ""),
            fhir_data=fhir_report
        )
        
        # Kaydet
        self.fhir_reports[resource_id] = diagnostic_report
        
        logger.info(f"FHIR DiagnosticReport oluşturuldu: {resource_id}")
        return diagnostic_report

    def get_fhir_report(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """FHIR raporu getir"""
        if resource_id not in self.fhir_reports:
            return None
        
        return self.fhir_reports[resource_id].fhir_data

    def get_patient_fhir_reports(self, nash_id: str) -> List[Dict[str, Any]]:
        """Hastanın FHIR raporlarını getir"""
        reports = []
        
        for report in self.fhir_reports.values():
            if report.nash_id == nash_id:
                reports.append(report.fhir_data)
        
        # Tarihe göre sırala
        reports.sort(key=lambda x: x.get("issued", ""), reverse=True)
        
        return reports

    def get_nash_id_from_mrn(self, mrn: str) -> Optional[str]:
        """MRN'den Nash ID al"""
        return self.nash_mapping.get(mrn)

    def get_anonymized_patient(self, nash_id: str) -> Optional[AnonymizedPatient]:
        """Anonimleştirilmiş hasta verisini getir"""
        return self.anonymized_patients.get(nash_id)

    def get_data_summary(self) -> Dict[str, Any]:
        """Veri özeti getir"""
        return {
            "anonymized_patients": len(self.anonymized_patients),
            "suv_trend_logs": sum(len(logs) for logs in self.suv_trend_logs.values()),
            "fhir_reports": len(self.fhir_reports),
            "nash_mappings": len(self.nash_mapping),
            "last_updated": datetime.now().isoformat()
        }

    def export_fhir_bundle(self, nash_id: str) -> Dict[str, Any]:
        """FHIR Bundle oluştur (hasta için tüm veriler)"""
        bundle_id = str(uuid.uuid4())
        
        # Hasta verisi
        patient_data = self.get_anonymized_patient(nash_id)
        if not patient_data:
            return {"error": "Hasta bulunamadı"}
        
        # FHIR Patient resource
        fhir_patient = {
            "resourceType": "Patient",
            "id": nash_id,
            "gender": patient_data.gender,
            "birthDate": "1900-01-01",  # Anonimleştirilmiş
            "meta": {
                "tag": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                        "code": "HCOMPL",
                        "display": "healthcare compliance"
                    }
                ]
            }
        }
        
        # FHIR DiagnosticReports
        diagnostic_reports = self.get_patient_fhir_reports(nash_id)
        
        # FHIR Bundle oluştur
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": [
                {
                    "resource": fhir_patient
                }
            ]
        }
        
        # DiagnosticReport'ları ekle
        for report in diagnostic_reports:
            bundle["entry"].append({
                "resource": report
            })
        
        return bundle

# Global data manager instance
data_manager = DataManager()

# Kullanım örneği
if __name__ == "__main__":
    # Test hasta verisi
    patient_data = PatientData(
        patient_id="P001",
        name="John",
        surname="Doe",
        birth_date="1980-01-01",
        gender="male",
        mrn="MRN123456",
        study_date=datetime.now(),
        study_type="FDG-PET/CT"
    )
    
    # Anonimleştir
    anonymized = data_manager.anonymize_patient_data(patient_data)
    print(f"Anonimleştirildi - Nash ID: {anonymized.nash_id}")
    
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
    print(f"SUV log eklendi: {suv_log.log_id}")
    
    # Trend verilerini al
    trend_data = data_manager.get_suv_trend_data(anonymized.nash_id)
    print(f"Trend verileri: {trend_data['summary']}")
    
    # FHIR raporu oluştur
    report_data = {
        "findings": ["Primer tümör tespit edildi"],
        "conclusion": "Malign lezyon",
        "study_date": datetime.now().isoformat()
    }
    
    fhir_report = data_manager.create_fhir_diagnostic_report(anonymized.nash_id, report_data)
    print(f"FHIR raporu oluşturuldu: {fhir_report.resource_id}")
