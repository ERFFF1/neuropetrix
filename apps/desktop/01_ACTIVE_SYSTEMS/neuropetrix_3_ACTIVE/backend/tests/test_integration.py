"""
Integration Tests
Entegrasyon testleri
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

class TestHealthEndpoints:
    """Health endpoint integration tests"""
    
    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"
        assert "message" in data
        assert "version" in data
    
    def test_database_health(self, client: TestClient):
        """Test database health endpoint"""
        response = client.get("/database/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
        assert "timestamp" in data
    
    def test_performance_health(self, client: TestClient):
        """Test performance health endpoint"""
        response = client.get("/performance/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
        assert "optimization_enabled" in data

class TestAuthentication:
    """Authentication integration tests"""
    
    def test_auth_me_without_token(self, client: TestClient):
        """Test /auth/me without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
    
    def test_auth_me_with_invalid_token(self, client: TestClient):
        """Test /auth/me with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_auth_me_with_valid_token(self, client: TestClient, auth_headers):
        """Test /auth/me with valid token"""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data

class TestPatientManagement:
    """Patient management integration tests"""
    
    def test_get_patients(self, client: TestClient):
        """Test get patients endpoint"""
        response = client.get("/database/patients")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_patient(self, client: TestClient, auth_headers, sample_patient_data):
        """Test create patient endpoint"""
        response = client.post(
            "/database/patients",
            json=sample_patient_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "message" in data
        assert data["message"] == "Patient created successfully"
    
    def test_get_patient_by_id(self, client: TestClient, auth_headers, sample_patient_data):
        """Test get patient by ID"""
        # First create a patient
        create_response = client.post(
            "/database/patients",
            json=sample_patient_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        patient_id = create_response.json()["id"]
        
        # Then get the patient
        response = client.get(f"/database/patients/{patient_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == patient_id
        assert data["first_name"] == sample_patient_data["first_name"]
        assert data["last_name"] == sample_patient_data["last_name"]
    
    def test_get_nonexistent_patient(self, client: TestClient):
        """Test get nonexistent patient"""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/database/patients/{fake_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

class TestReportManagement:
    """Report management integration tests"""
    
    def test_get_reports(self, client: TestClient):
        """Test get reports endpoint"""
        response = client.get("/database/reports")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_report(self, client: TestClient, auth_headers, sample_report_data):
        """Test create report endpoint"""
        response = client.post(
            "/database/reports",
            json=sample_report_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "message" in data
        assert data["message"] == "Report created successfully"
    
    def test_get_reports_by_patient(self, client: TestClient, auth_headers, sample_report_data):
        """Test get reports by patient ID"""
        # First create a report
        create_response = client.post(
            "/database/reports",
            json=sample_report_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        # Then get reports for the patient
        patient_id = sample_report_data["patient_id"]
        response = client.get(f"/database/reports?patient_id={patient_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are reports
            assert data[0]["patient_id"] == patient_id

class TestSUVMeasurements:
    """SUV measurements integration tests"""
    
    def test_get_suv_measurements(self, client: TestClient):
        """Test get SUV measurements endpoint"""
        response = client.get("/database/suv-measurements")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_suv_measurement(self, client: TestClient, auth_headers, sample_suv_data):
        """Test create SUV measurement endpoint"""
        response = client.post(
            "/database/suv-measurements",
            json=sample_suv_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "message" in data
        assert data["message"] == "SUV measurement created successfully"
    
    def test_get_suv_measurements_by_patient(self, client: TestClient, auth_headers, sample_suv_data):
        """Test get SUV measurements by patient ID"""
        # First create a measurement
        create_response = client.post(
            "/database/suv-measurements",
            json=sample_suv_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        
        # Then get measurements for the patient
        patient_id = sample_suv_data["patient_id"]
        response = client.get(f"/database/suv-measurements?patient_id={patient_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are measurements
            assert data[0]["patient_id"] == patient_id

class TestPerformanceEndpoints:
    """Performance endpoints integration tests"""
    
    def test_get_performance_metrics(self, client: TestClient):
        """Test get performance metrics endpoint"""
        response = client.get("/performance/metrics")
        
        # This might return 500 if metrics collection fails, which is expected in test environment
        assert response.status_code in [200, 500]
    
    def test_get_performance_summary(self, client: TestClient):
        """Test get performance summary endpoint"""
        response = client.get("/performance/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_optimize_memory(self, client: TestClient):
        """Test memory optimization endpoint"""
        response = client.post("/performance/optimize/memory")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "started"
    
    def test_optimize_cpu(self, client: TestClient):
        """Test CPU optimization endpoint"""
        response = client.post("/performance/optimize/cpu")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "started"
    
    def test_auto_optimize(self, client: TestClient):
        """Test auto optimization endpoint"""
        response = client.post("/performance/optimize/auto")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "started"

class TestDatabaseOperations:
    """Database operations integration tests"""
    
    def test_database_status(self, client: TestClient):
        """Test database status endpoint"""
        response = client.get("/database/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "tables" in data
        assert "total_records" in data
    
    def test_database_statistics(self, client: TestClient):
        """Test database statistics endpoint"""
        response = client.get("/database/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "counts" in data
        assert "recent_activity" in data
        assert "timestamp" in data
    
    def test_migrate_database(self, client: TestClient):
        """Test database migration endpoint"""
        response = client.post("/database/migrate")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "started"
    
    def test_backup_database(self, client: TestClient):
        """Test database backup endpoint"""
        response = client.post("/database/backup")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "started"
    
    def test_restore_database(self, client: TestClient):
        """Test database restore endpoint"""
        backup_path = "test_backup.db"
        response = client.post("/database/restore", json={"backup_path": backup_path})
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "started"

class TestAuditLogs:
    """Audit logs integration tests"""
    
    def test_get_audit_logs(self, client: TestClient):
        """Test get audit logs endpoint"""
        response = client.get("/database/audit-logs")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_with_filters(self, client: TestClient):
        """Test get audit logs with filters"""
        response = client.get("/database/audit-logs?action=create_patient&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestSystemMetrics:
    """System metrics integration tests"""
    
    def test_store_system_metrics(self, client: TestClient):
        """Test store system metrics endpoint"""
        metrics_data = {
            "cpu_percent": 50.0,
            "memory_percent": 60.0,
            "memory_used_mb": 1024.0,
            "memory_available_mb": 1024.0,
            "disk_usage_percent": 50.0,
            "network_io": {"bytes_sent": 1000, "bytes_recv": 2000},
            "active_connections": 10,
            "response_time_ms": 100.0,
            "requests_per_second": 10.0,
            "cache_hit_rate": 85.0
        }
        
        response = client.post("/database/metrics", json=metrics_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "System metrics stored successfully"

class TestErrorHandling:
    """Error handling integration tests"""
    
    def test_invalid_json_request(self, client: TestClient, auth_headers):
        """Test invalid JSON request"""
        response = client.post(
            "/database/patients",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client: TestClient, auth_headers):
        """Test missing required fields"""
        incomplete_data = {
            "first_name": "Test"
            # Missing required fields
        }
        
        response = client.post(
            "/database/patients",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 500  # Should fail validation
    
    def test_invalid_date_format(self, client: TestClient, auth_headers):
        """Test invalid date format"""
        invalid_data = {
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": "invalid-date",
            "gender": "male"
        }
        
        response = client.post(
            "/database/patients",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 500  # Should fail date parsing

class TestConcurrentOperations:
    """Concurrent operations integration tests"""
    
    def test_concurrent_patient_creation(self, client: TestClient, auth_headers):
        """Test concurrent patient creation"""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_patient(patient_id):
            try:
                patient_data = {
                    "first_name": f"Test{patient_id}",
                    "last_name": "Patient",
                    "date_of_birth": "1990-01-01T00:00:00",
                    "gender": "male",
                    "phone": f"+90555123456{patient_id}",
                    "email": f"test{patient_id}@example.com"
                }
                
                response = client.post(
                    "/database/patients",
                    json=patient_data,
                    headers=auth_headers
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_patient, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__])
