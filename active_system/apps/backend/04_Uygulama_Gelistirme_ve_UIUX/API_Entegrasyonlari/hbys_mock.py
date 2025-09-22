from typing import Dict, Any, List
import json
from datetime import datetime

class HBYSMock:
    """HBYS (Hastane Bilgi Yönetim Sistemi) Mock API"""
    
    def __init__(self):
        self.patients = {
            "P-001": {
                "id": "P-001",
                "name": "Ahmet Yılmaz",
                "age": 65,
                "gender": "M",
                "diagnosis": "Lung cancer",
                "admission_date": "2024-01-15",
                "room": "301"
            },
            "P-002": {
                "id": "P-002", 
                "name": "Fatma Demir",
                "age": 45,
                "gender": "F",
                "diagnosis": "Lymphoma",
                "admission_date": "2024-01-14",
                "room": "205"
            }
        }
        
        self.laboratory_results = {
            "P-001": {
                "glucose": 110,
                "creatinine": 0.9,
                "egfr": 90,
                "psa": None,
                "cea": 5.2,
                "ca125": None
            },
            "P-002": {
                "glucose": 95,
                "creatinine": 0.8,
                "egfr": 95,
                "psa": None,
                "cea": 2.1,
                "ca125": 15.3
            }
        }
    
    def get_patient_info(self, patient_id: str) -> Dict[str, Any]:
        """Hasta bilgilerini getir"""
        try:
            patient = self.patients.get(patient_id)
            if not patient:
                return {
                    "success": False,
                    "error": "Patient not found"
                }
            
            return {
                "success": True,
                "patient": patient
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_laboratory_results(self, patient_id: str) -> Dict[str, Any]:
        """Laboratuvar sonuçlarını getir"""
        try:
            results = self.laboratory_results.get(patient_id)
            if not results:
                return {
                    "success": False,
                    "error": "Laboratory results not found"
                }
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_medication_list(self, patient_id: str) -> Dict[str, Any]:
        """İlaç listesini getir"""
        try:
            # Simüle edilmiş ilaç listesi
            medications = [
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "twice daily",
                    "start_date": "2024-01-10"
                },
                {
                    "name": "Aspirin",
                    "dosage": "100mg", 
                    "frequency": "once daily",
                    "start_date": "2024-01-12"
                }
            ]
            
            return {
                "success": True,
                "medications": medications
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_patient_status(self, patient_id: str, status: str) -> Dict[str, Any]:
        """Hasta durumunu güncelle"""
        try:
            if patient_id not in self.patients:
                return {
                    "success": False,
                    "error": "Patient not found"
                }
            
            self.patients[patient_id]["status"] = status
            self.patients[patient_id]["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "Patient status updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


