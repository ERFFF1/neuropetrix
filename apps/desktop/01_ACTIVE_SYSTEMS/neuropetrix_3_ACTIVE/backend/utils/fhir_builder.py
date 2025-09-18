"""
NeuroPETRIX FHIR Builder Utility
Diagnostic reports ve evidence annexes için FHIR resource'ları oluşturur
"""

import base64
import datetime as dt
from typing import Dict, Any, Optional, List

def diagnostic_report(patient_id: str, report_text: str, report_type: str = "TSNM") -> Dict[str, Any]:
    """
    TSNM Diagnostic Report FHIR resource'ı oluştur
    
    Args:
        patient_id: Hasta ID'si
        report_text: Rapor metni
        report_type: Rapor tipi (TSNM, staging, followup)
    
    Returns:
        FHIR DiagnosticReport resource
    """
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    return {
        "resourceType": "DiagnosticReport",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "68608-9",
                    "display": "PET scan whole body"
                }
            ],
            "text": f"{report_type} PET/CT Report"
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": now,
        "issued": now,
        "conclusion": report_text,
        "presentedForm": [
            {
                "contentType": "text/plain",
                "data": base64.b64encode(report_text.encode()).decode(),
                "title": f"{report_type}_report.txt"
            }
        ],
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/DiagnosticReport"],
            "tag": [
                {
                    "system": "http://neuropetrix.com/tags",
                    "code": report_type.lower(),
                    "display": report_type
                }
            ]
        }
    }

def evidence_annex_docref(patient_id: str, pdf_bytes: bytes, evidence_type: str = "PICO_GRADE") -> Dict[str, Any]:
    """
    Evidence Annex DocumentReference FHIR resource'ı oluştur
    
    Args:
        patient_id: Hasta ID'si
        pdf_bytes: PDF dosya bytes
        evidence_type: Evidence tipi (PICO_GRADE, literature_review, clinical_guidelines)
    
    Returns:
        FHIR DocumentReference resource
    """
    b64 = base64.b64encode(pdf_bytes).decode()
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    return {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "11506-3",
                    "display": "Progress note"
                }
            ],
            "text": f"Evidence Annex ({evidence_type})"
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "date": now,
        "content": [
            {
                "attachment": {
                    "contentType": "application/pdf",
                    "data": b64,
                    "title": f"evidence_annex_{evidence_type.lower()}.pdf",
                    "size": len(pdf_bytes)
                }
            }
        ],
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/DocumentReference"],
            "tag": [
                {
                    "system": "http://neuropetrix.com/evidence",
                    "code": evidence_type.lower(),
                    "display": evidence_type
                }
            ]
        }
    }

def create_workflow_bundle(patient_id: str, case_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Workflow sonuçları için FHIR Bundle oluştur
    
    Args:
        patient_id: Hasta ID'si
        case_id: Vaka ID'si
        workflow_data: Workflow sonuç verileri
    
    Returns:
        FHIR Bundle resource
    """
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    # Ana diagnostic report
    report_text = f"""
TSNM Report - Case {case_id}
Patient ID: {patient_id}
Generated: {now}

Workflow Results:
{workflow_data.get('workflow_result', 'No workflow data')}
    """.strip()
    
    diagnostic_report_resource = diagnostic_report(patient_id, report_text, "TSNM")
    
    # Bundle oluştur
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "identifier": {
            "system": "http://neuropetrix.com/cases",
            "value": case_id
        },
        "timestamp": now,
        "entry": [
            {
                "resource": diagnostic_report_resource
            }
        ]
    }
    
    # Evidence annex varsa ekle
    if 'evidence_result' in workflow_data:
        evidence_text = f"Evidence Summary for Case {case_id}"
        evidence_bytes = evidence_text.encode()
        evidence_docref = evidence_annex_docref(patient_id, evidence_bytes, "PICO_GRADE")
        bundle["entry"].append({"resource": evidence_docref})
    
    return bundle

def patient_resource(patient_id: str, patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hasta FHIR resource'ı oluştur
    
    Args:
        patient_id: Hasta ID'si
        patient_data: Hasta bilgileri
    
    Returns:
        FHIR Patient resource
    """
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    return {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [
            {
                "system": "http://neuropetrix.com/patients",
                "value": patient_id
            }
        ],
        "active": True,
        "name": [
            {
                "use": "official",
                "text": patient_data.get('name', 'Unknown')
            }
        ],
        "gender": patient_data.get('gender', 'unknown'),
        "birthDate": patient_data.get('birth_date'),
        "meta": {
            "lastUpdated": now,
            "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
        }
    }

def observation_resource(patient_id: str, observation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Observation FHIR resource'ı oluştur (SUV değerleri için)
    
    Args:
        patient_id: Hasta ID'si
        observation_data: Observation verileri
    
    Returns:
        FHIR Observation resource
    """
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    return {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "81258-0",
                    "display": "SUV max"
                }
            ],
            "text": "SUV Maximum Value"
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": now,
        "issued": now,
        "valueQuantity": {
            "value": observation_data.get('suv_value', 0.0),
            "unit": "g/mL",
            "system": "http://unitsofmeasure.org",
            "code": "g/mL"
        },
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Observation"]
        }
    }


