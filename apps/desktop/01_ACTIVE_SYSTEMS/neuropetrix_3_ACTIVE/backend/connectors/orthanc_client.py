import requests
import json
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class OrthancClient:
    """Orthanc PACS client for DICOM operations"""
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        self.base_url = base_url or os.getenv("ORTHANC_URL", "http://localhost:8042")
        self.username = username or os.getenv("ORTHANC_USERNAME")
        self.password = password or os.getenv("ORTHANC_PASSWORD")
        
        # Setup session
        self.session = requests.Session()
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
    
    def health_check(self) -> Dict:
        """Check Orthanc server health"""
        try:
            response = self.session.get(f"{self.base_url}/system")
            response.raise_for_status()
            return {
                "status": "healthy",
                "version": response.json().get("Version"),
                "uptime": response.json().get("Uptime")
            }
        except Exception as e:
            logger.error(f"Orthanc health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    def get_patients(self) -> List[Dict]:
        """Get list of patients"""
        try:
            response = self.session.get(f"{self.base_url}/patients")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get patients: {str(e)}")
            return []
    
    def get_studies(self, patient_id: str) -> List[Dict]:
        """Get studies for a patient"""
        try:
            response = self.session.get(f"{self.base_url}/patients/{patient_id}/studies")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get studies for patient {patient_id}: {str(e)}")
            return []
    
    def get_series(self, study_id: str) -> List[Dict]:
        """Get series for a study"""
        try:
            response = self.session.get(f"{self.base_url}/studies/{study_id}/series")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get series for study {study_id}: {str(e)}")
            return []
    
    def get_instances(self, series_id: str) -> List[Dict]:
        """Get instances for a series"""
        try:
            response = self.session.get(f"{self.base_url}/series/{series_id}/instances")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get instances for series {series_id}: {str(e)}")
            return []
    
    def download_dicom(self, instance_id: str, output_path: str) -> bool:
        """Download DICOM file"""
        try:
            response = self.session.get(f"{self.base_url}/instances/{instance_id}/file")
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"DICOM downloaded to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download DICOM {instance_id}: {str(e)}")
            return False
    
    def upload_dicom(self, file_path: str) -> Optional[str]:
        """Upload DICOM file to Orthanc"""
        try:
            with open(file_path, 'rb') as f:
                response = self.session.post(
                    f"{self.base_url}/instances",
                    data=f.read(),
                    headers={'Content-Type': 'application/dicom'}
                )
                response.raise_for_status()
                
                instance_id = response.json().get("ID")
                logger.info(f"DICOM uploaded with ID: {instance_id}")
                return instance_id
                
        except Exception as e:
            logger.error(f"Failed to upload DICOM {file_path}: {str(e)}")
            return None
    
    def get_dicom_tags(self, instance_id: str) -> Dict:
        """Get DICOM tags for an instance"""
        try:
            response = self.session.get(f"{self.base_url}/instances/{instance_id}/tags")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get tags for instance {instance_id}: {str(e)}")
            return {}
    
    def search_patients(self, query: str) -> List[Dict]:
        """Search patients by name or ID"""
        try:
            response = self.session.post(
                f"{self.base_url}/tools/find",
                json={
                    "Level": "Patient",
                    "Query": {
                        "PatientName": query,
                        "PatientID": query
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to search patients: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get Orthanc server statistics"""
        try:
            response = self.session.get(f"{self.base_url}/statistics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}

# Global Orthanc client instance
orthanc_client = OrthancClient()


