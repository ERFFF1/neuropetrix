#!/usr/bin/env python3
"""
NeuroPETRIX v2.0 - End-to-End Test Scenarios
============================================

3 temel test senaryosu:
(A) DICOM YOK → Staging 
(B) DICOM VAR → Response (PERCIST)
(C) DICOM VAR → Lymphoma follow-up (Deauville)
"""

import requests
import json
import time
from datetime import datetime

# Server URL
BASE_URL = "http://localhost:8000"

def print_response(response, title):
    """Response'u güzel formatta yazdır"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
    else:
        print(f"❌ Error: {response.text}")

def test_scenario_a_no_dicom():
    """
    (A) DICOM YOK → Staging (PERCIST/Deauville yok)
    """
    print("\n🧪 TEST SCENARIO A: NO DICOM → STAGING")
    
    # 1. Patient Intake
    patient_data = {
        "patient_id": "NPX-001",
        "icd10": "C34.9",
        "clinical_goal": "staging",
        "hbys": {
            "ECOG": 1,
            "eGFR": 78,
            "BloodGlucose_mgdl": 96,
            "allergies": [],
            "meds": []
        }
    }
    
    response = requests.post(f"{BASE_URL}/intake/patient", json=patient_data)
    print_response(response, "1. Patient Intake")
    
    # 2. Evidence Build
    evidence_data = {
        "pico_seed": {
            "population": "Lung cancer patients",
            "intervention": "FDG PET/CT",
            "comparison": "Standard imaging",
            "outcome": "Staging accuracy"
        },
        "icd10": "C34.9",
        "hbys_ref": "NPX-001"
    }
    
    response = requests.post(f"{BASE_URL}/evidence/search", json=evidence_data)
    print_response(response, "2. Evidence Search")
    
    # 3. Report Compose (No Imaging)
    report_data = {
        "patient_id": "NPX-001",
        "include_imaging": False,
        "include_evidence": True,
        "report_format": "all"
    }
    
    response = requests.post(f"{BASE_URL}/report/compose", json=report_data)
    print_response(response, "3. Report Compose (No DICOM)")

def test_scenario_b_dicom_response():
    """
    (B) DICOM VAR → Response (PERCIST hesaplanır)
    """
    print("\n🧪 TEST SCENARIO B: DICOM + RESPONSE (PERCIST)")
    
    # 1. Patient Intake
    patient_data = {
        "patient_id": "NPX-002", 
        "icd10": "C34.9",
        "clinical_goal": "response",
        "hbys": {
            "ECOG": 0,
            "eGFR": 85,
            "BloodGlucose_mgdl": 102,
            "allergies": [],
            "meds": ["Cisplatin", "Etoposide"]
        }
    }
    
    response = requests.post(f"{BASE_URL}/intake/patient", json=patient_data)
    print_response(response, "1. Patient Intake")
    
    # 2. Imaging Pipeline (Mock)
    imaging_data = {
        "patient_id": "NPX-002",
        "dicom_files": ["./data/mock_dicom/series_001.dcm", "./data/mock_dicom/series_002.dcm"],
        "case_meta": {
            "patient_id": "NPX-002",
            "study_uid": "1.2.3.4.5",
            "icd10": "C34.9",
            "clinical_goal": "response",
            "pico": {
                "P": "Lung cancer patients on treatment",
                "I": "FDG PET/CT",
                "C": "prev PET",
                "O": "PERCIST response"
            },
            "hints": {
                "structures_of_interest": ["primary_tumor", "nodes"]
            },
            "acquisition": {
                "tracer": "FDG",
                "dose_MBq": 300,
                "blood_glucose_mgdl": 102,
                "uptake_time_min": 62
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/imaging/run", json=imaging_data)
    print_response(response, "2. Imaging Pipeline")
    
    # 3. Report Compose (With Imaging)
    report_data = {
        "patient_id": "NPX-002",
        "include_imaging": True,
        "include_evidence": True,
        "report_format": "all"
    }
    
    response = requests.post(f"{BASE_URL}/report/compose", json=report_data)
    print_response(response, "3. Report Compose (With PERCIST)")

def test_scenario_c_lymphoma_deauville():
    """
    (C) DICOM VAR → Lenfoma follow-up (Deauville hesaplanır)
    """
    print("\n🧪 TEST SCENARIO C: DICOM + LYMPHOMA FOLLOWUP (DEAUVILLE)")
    
    # 1. Patient Intake
    patient_data = {
        "patient_id": "NPX-003",
        "icd10": "C81.9",  # Hodgkin lymphoma
        "clinical_goal": "lymphoma_followup",
        "hbys": {
            "ECOG": 0,
            "eGFR": 90,
            "BloodGlucose_mgdl": 95,
            "allergies": [],
            "meds": ["ABVD Protocol"]
        }
    }
    
    response = requests.post(f"{BASE_URL}/intake/patient", json=patient_data)
    print_response(response, "1. Patient Intake")
    
    # 2. Imaging Pipeline (Mock)
    imaging_data = {
        "patient_id": "NPX-003",
        "dicom_files": ["./data/mock_dicom/lymphoma_001.dcm", "./data/mock_dicom/lymphoma_002.dcm"],
        "case_meta": {
            "patient_id": "NPX-003",
            "study_uid": "1.2.3.4.6",
            "icd10": "C81.9",
            "clinical_goal": "lymphoma_followup",
            "pico": {
                "P": "Hodgkin lymphoma patients on treatment",
                "I": "FDG PET/CT",
                "C": "Baseline PET",
                "O": "Deauville response"
            },
            "hints": {
                "structures_of_interest": ["lymph_nodes", "spleen", "bone_marrow"]
            },
            "acquisition": {
                "tracer": "FDG",
                "dose_MBq": 370,
                "blood_glucose_mgdl": 95,
                "uptake_time_min": 60
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/imaging/run", json=imaging_data)
    print_response(response, "2. Imaging Pipeline")
    
    # 3. Report Compose (With Imaging)
    report_data = {
        "patient_id": "NPX-003",
        "include_imaging": True,
        "include_evidence": True,
        "report_format": "all"
    }
    
    response = requests.post(f"{BASE_URL}/report/compose", json=report_data)
    print_response(response, "3. Report Compose (With Deauville)")

def test_health_check():
    """Health check endpoint'i test et"""
    print("\n🔍 HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    
    response = requests.get(f"{BASE_URL}/api/status")
    print_response(response, "API Status")

def main():
    """Test runner"""
    print("🚀 NEUROPETRIX v2.0 - END-TO-END TESTS")
    print("=" * 60)
    print(f"Server: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Health check
        test_health_check()
        
        # 3 Ana test senaryosu
        test_scenario_a_no_dicom()
        test_scenario_b_dicom_response() 
        test_scenario_c_lymphoma_deauville()
        
        print(f"\n{'='*60}")
        print("✅ ALL TESTS COMPLETED")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")

if __name__ == "__main__":
    main()
