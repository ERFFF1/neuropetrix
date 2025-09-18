from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/report", tags=["Report Generation"])

class ReportRequest(BaseModel):
    patient_id: str
    include_imaging: bool = False
    include_evidence: bool = True
    report_format: str = "all"  # tsnm, annex, fhir, all

class ReportResult(BaseModel):
    patient_id: str
    report_id: str
    generated_at: datetime
    tsnm_report: Optional[Dict[str, Any]] = None
    annex_report: Optional[Dict[str, Any]] = None
    fhir_report: Optional[Dict[str, Any]] = None
    status: str
    processing_time: float = 0.0

@router.post("/compose")
async def compose_report(report_request: ReportRequest):
    """
    Decision Composer → TSNM/Annex/FHIR rapor üret
    """
    import time
    start_time = time.time()
    
    try:
        # Case verilerini yükle
        case_data = await _load_case_data(report_request.patient_id)
        
        # Decision composer çalıştır
        decision_packet = await _run_decision_composer(case_data)
        
        # Raporları oluştur
        tsnm_report = None
        annex_report = None
        fhir_report = None
        
        if report_request.report_format in ["tsnm", "all"]:
            tsnm_report = await _generate_tsnm_report(case_data, decision_packet)
        
        if report_request.report_format in ["annex", "all"]:
            annex_report = await _generate_annex_report(case_data, decision_packet)
        
        if report_request.report_format in ["fhir", "all"]:
            fhir_report = await _generate_fhir_report(case_data, decision_packet)
        
        # Sonucu oluştur
        report_id = f"RPT-{report_request.patient_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        processing_time = time.time() - start_time
        
        report_result = ReportResult(
            patient_id=report_request.patient_id,
            report_id=report_id,
            generated_at=datetime.now(),
            tsnm_report=tsnm_report,
            annex_report=annex_report,
            fhir_report=fhir_report,
            status="completed",
            processing_time=processing_time
        )
        
        # Raporu kaydet
        await _save_report(report_request.patient_id, report_result)
        
        # Case meta'yı güncelle
        await _update_case_meta(report_request.patient_id, report_id)
        
        return report_result
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(status_code=500, detail=f"Report composition failed: {str(e)}")

async def _load_case_data(patient_id: str) -> Dict[str, Any]:
    """Case verilerini yükle"""
    case_dir = f"data/cases/{patient_id}"
    
    case_data = {}
    
    # Patient packet
    patient_file = f"{case_dir}/patient_packet.json"
    if os.path.exists(patient_file):
        with open(patient_file, "r") as f:
            case_data["patient"] = json.load(f)
    
    # Case meta
    meta_file = f"{case_dir}/case_meta.json"
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            case_data["meta"] = json.load(f)
    
    # Imaging result
    imaging_file = f"{case_dir}/imaging_result.json"
    if os.path.exists(imaging_file):
        with open(imaging_file, "r") as f:
            case_data["imaging"] = json.load(f)
    
    # Evidence packet
    evidence_file = f"{case_dir}/evidence_packet.json"
    if os.path.exists(evidence_file):
        with open(evidence_file, "r") as f:
            case_data["evidence"] = json.load(f)
    
    return case_data

async def _run_decision_composer(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decision composer çalıştır"""
    # TODO: Implement actual decision composer service
    clinical_goal = case_data.get("meta", {}).get("clinical_goal", "staging")
    imaging_available = case_data.get("meta", {}).get("imaging_available", False)
    
    decision_packet = {
        "clinical_goal": clinical_goal,
        "imaging_available": imaging_available,
        "ai_conclusion": "",
        "rationale_keys": [],
        "percist": None,
        "deauville": None,
        "qc_flags": []
    }
    
    if imaging_available and "imaging" in case_data:
        imaging_metrics = case_data["imaging"].get("imaging_metrics", {})
        clinical_metrics = imaging_metrics.get("clinical_metrics", {})
        
        if clinical_goal == "response" and "PERCIST" in clinical_metrics:
            decision_packet["percist"] = clinical_metrics["PERCIST"]
            decision_packet["ai_conclusion"] = f"PERCIST: {clinical_metrics['PERCIST']} - {clinical_metrics.get('category', '')}"
        
        elif clinical_goal == "lymphoma_followup" and "Deauville" in clinical_metrics:
            decision_packet["deauville"] = clinical_metrics["Deauville"]
            decision_packet["ai_conclusion"] = f"Deauville Score: {clinical_metrics['Deauville']} - {clinical_metrics.get('category', '')}"
        
        # QC flags
        qc_flags = case_data["imaging"].get("qc_flags", [])
        decision_packet["qc_flags"] = qc_flags
    
    # Evidence-based conclusion
    if "evidence" in case_data:
        evidence_level = case_data["evidence"].get("evidence_level", "Moderate")
        decision_packet["rationale_keys"].append(f"Evidence Level: {evidence_level}")
    
    # Default conclusion if no imaging
    if not decision_packet["ai_conclusion"]:
        if clinical_goal == "staging":
            decision_packet["ai_conclusion"] = "Initial staging assessment completed. Consider imaging for comprehensive evaluation."
        elif clinical_goal == "response":
            decision_packet["ai_conclusion"] = "Response assessment requires baseline and follow-up imaging for PERCIST evaluation."
        elif clinical_goal == "lymphoma_followup":
            decision_packet["ai_conclusion"] = "Lymphoma follow-up assessment completed. Deauville scoring requires imaging data."
    
    return decision_packet

async def _generate_tsnm_report(case_data: Dict[str, Any], decision_packet: Dict[str, Any]) -> Dict[str, Any]:
    """TSNM raporu oluştur"""
    patient = case_data.get("patient", {})
    meta = case_data.get("meta", {})
    
    tsnm_report = {
        "patient_id": patient.get("patient_id"),
        "icd10": patient.get("icd10"),
        "clinical_goal": meta.get("clinical_goal"),
        "findings": _generate_findings(case_data, decision_packet),
        "percist_category": decision_packet.get("percist"),
        "deauville_score": decision_packet.get("deauville"),
        "ai_conclusion": decision_packet.get("ai_conclusion"),
        "qc_flags": decision_packet.get("qc_flags", []),
        "report_type": "TSNM",
        "generated_at": datetime.now().isoformat()
    }
    
    return tsnm_report

def _generate_findings(case_data: Dict[str, Any], decision_packet: Dict[str, Any]) -> str:
    """Bulguları oluştur"""
    findings = []
    
    if "imaging" in case_data:
        imaging_metrics = case_data["imaging"].get("imaging_metrics", {})
        radiomics = imaging_metrics.get("radiomics", {})
        
        if radiomics:
            findings.append(f"SUVmax: {radiomics.get('SUVmax', 'N/A')} g/mL")
            findings.append(f"MTV: {radiomics.get('MTV', 'N/A')} cm³")
            findings.append(f"TLG: {radiomics.get('TLG', 'N/A')} g")
    
    if not findings:
        findings.append("No imaging data available for findings generation")
    
    return "; ".join(findings)

async def _generate_annex_report(case_data: Dict[str, Any], decision_packet: Dict[str, Any]) -> Dict[str, Any]:
    """Evidence Annex raporu oluştur"""
    evidence = case_data.get("evidence", {})
    
    annex_report = {
        "pico_question": evidence.get("pico_question"),
        "grade_summary": evidence.get("grade_summary"),
        "references": evidence.get("references", []),
        "toxicity_notes": evidence.get("toxicity_notes"),
        "evidence_level": evidence.get("evidence_level"),
        "report_type": "Evidence Annex",
        "generated_at": datetime.now().isoformat()
    }
    
    return annex_report

async def _generate_fhir_report(case_data: Dict[str, Any], decision_packet: Dict[str, Any]) -> Dict[str, Any]:
    """FHIR DiagnosticReport oluştur"""
    patient = case_data.get("patient", {})
    meta = case_data.get("meta", {})
    
    # DiagnosticReport
    diagnostic_report = {
        "resourceType": "DiagnosticReport",
        "status": "final",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "18748-4",
                "display": "Diagnostic imaging study report"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient.get('patient_id')}"
        },
        "effectiveDateTime": datetime.now().isoformat(),
        "issued": datetime.now().isoformat(),
        "result": []
    }
    
    # Observations
    observations = []
    
    if "imaging" in case_data:
        imaging_metrics = case_data["imaging"].get("imaging_metrics", {})
        radiomics = imaging_metrics.get("radiomics", {})
        
        if radiomics:
            # SUVmax observation
            if "SUVmax" in radiomics:
                observations.append({
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "81258-6",
                            "display": "SUVmax"
                        }]
                    },
                    "valueQuantity": {
                        "value": radiomics["SUVmax"],
                        "unit": "g/mL",
                        "system": "http://unitsofmeasure.org",
                        "code": "g/mL"
                    }
                })
            
            # MTV observation
            if "MTV" in radiomics:
                observations.append({
                    "resourceType": "Observation",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "81259-4",
                            "display": "MTV"
                        }]
                    },
                    "valueQuantity": {
                        "value": radiomics["MTV"],
                        "unit": "cm³",
                        "system": "http://unitsofmeasure.org",
                        "code": "cm3"
                    }
                })
    
    fhir_report = {
        "diagnostic_report": diagnostic_report,
        "observations": observations,
        "report_type": "FHIR",
        "generated_at": datetime.now().isoformat()
    }
    
    return fhir_report

async def _save_report(patient_id: str, report_result: ReportResult):
    """Raporu kaydet"""
    case_dir = f"data/cases/{patient_id}"
    os.makedirs(case_dir, exist_ok=True)
    
    report_file = f"{case_dir}/report_result.json"
    with open(report_file, "w") as f:
        json.dump(report_result.dict(), f, default=str, indent=2)

async def _update_case_meta(patient_id: str, report_id: str):
    """Case meta'yı güncelle"""
    case_dir = f"data/cases/{patient_id}"
    meta_file = f"{case_dir}/case_meta.json"
    
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            case_meta = json.load(f)
        
        case_meta["report_generated"] = True
        case_meta["report_id"] = report_id
        case_meta["report_generated_at"] = datetime.now().isoformat()
        
        with open(meta_file, "w") as f:
            json.dump(case_meta, f, indent=2)

@router.get("/{patient_id}")
async def get_report(patient_id: str):
    """Hasta için raporu getir"""
    try:
        case_dir = f"data/cases/{patient_id}"
        report_file = f"{case_dir}/report_result.json"
        
        if not os.path.exists(report_file):
            raise HTTPException(status_code=404, detail="Report not found")
        
        with open(report_file, "r") as f:
            report = json.load(f)
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")

@router.get("/{patient_id}/tsnm")
async def get_tsnm_report(patient_id: str):
    """TSNM raporunu getir"""
    try:
        report = await get_report(patient_id)
        return report.get("tsnm_report")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TSNM report: {str(e)}")

@router.get("/{patient_id}/annex")
async def get_annex_report(patient_id: str):
    """Annex raporunu getir"""
    try:
        report = await get_report(patient_id)
        return report.get("annex_report")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Annex report: {str(e)}")

@router.get("/{patient_id}/fhir")
async def get_fhir_report(patient_id: str):
    """FHIR raporunu getir"""
    try:
        report = await get_report(patient_id)
        return report.get("fhir_report")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get FHIR report: {str(e)}")
