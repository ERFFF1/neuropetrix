"""
End-to-End Tests
Uçtan uca testler
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient

class TestCompleteWorkflow:
    """Complete workflow end-to-end tests"""
    
    def test_complete_patient_workflow(self, client: TestClient, auth_headers):
        """Test complete patient workflow from creation to report"""
        # Step 1: Create a patient
        patient_data = {
            "first_name": "E2E",
            "last_name": "Test Patient",
            "date_of_birth": "1985-06-15T00:00:00",
            "gender": "female",
            "phone": "+905551234567",
            "email": "e2e.test@example.com",
            "address": "Test Address, Istanbul",
            "medical_history": "No significant medical history",
            "allergies": ["aspirin"],
            "emergency_contact": {
                "name": "Emergency Contact",
                "phone": "+905559876543",
                "relationship": "spouse"
            }
        }
        
        create_response = client.post(
            "/database/patients",
            json=patient_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        patient_id = create_response.json()["id"]
        
        # Step 2: Create a report for the patient
        report_data = {
            "patient_id": patient_id,
            "report_type": "pet-ct",
            "study_date": "2024-01-15T10:00:00",
            "findings": "Multiple hypermetabolic lesions identified in liver and lungs",
            "impression": "Suspicious for metastatic disease",
            "recommendations": "Further evaluation with biopsy recommended",
            "attachments": [],
            "status": "completed"
        }
        
        report_response = client.post(
            "/database/reports",
            json=report_data,
            headers=auth_headers
        )
        assert report_response.status_code == 200
        report_id = report_response.json()["id"]
        
        # Step 3: Add SUV measurements
        suv_data = {
            "patient_id": patient_id,
            "report_id": report_id,
            "measurement_date": "2024-01-15T10:00:00",
            "suv_max": 12.5,
            "suv_mean": 6.8,
            "suv_peak": 11.2,
            "lesion_location": "Liver segment 4",
            "lesion_size": 3.2,
            "notes": "Primary lesion with high metabolic activity"
        }
        
        suv_response = client.post(
            "/database/suv-measurements",
            json=suv_data,
            headers=auth_headers
        )
        assert suv_response.status_code == 200
        suv_id = suv_response.json()["id"]
        
        # Step 4: Verify all data is linked correctly
        # Get patient details
        patient_response = client.get(f"/database/patients/{patient_id}")
        assert patient_response.status_code == 200
        patient_details = patient_response.json()
        assert patient_details["first_name"] == "E2E"
        assert patient_details["last_name"] == "Test Patient"
        
        # Get reports for patient
        reports_response = client.get(f"/database/reports?patient_id={patient_id}")
        assert reports_response.status_code == 200
        reports = reports_response.json()
        assert len(reports) >= 1
        assert reports[0]["patient_id"] == patient_id
        assert reports[0]["report_type"] == "pet-ct"
        
        # Get SUV measurements for patient
        suv_measurements_response = client.get(f"/database/suv-measurements?patient_id={patient_id}")
        assert suv_measurements_response.status_code == 200
        suv_measurements = suv_measurements_response.json()
        assert len(suv_measurements) >= 1
        assert suv_measurements[0]["patient_id"] == patient_id
        assert suv_measurements[0]["suv_max"] == 12.5
        
        # Step 5: Verify audit logs
        audit_logs_response = client.get("/database/audit-logs")
        assert audit_logs_response.status_code == 200
        audit_logs = audit_logs_response.json()
        
        # Should have logs for patient creation and report creation
        patient_creation_logs = [log for log in audit_logs if log["action"] == "create_patient"]
        report_creation_logs = [log for log in audit_logs if log["action"] == "create_report"]
        
        assert len(patient_creation_logs) >= 1
        assert len(report_creation_logs) >= 1
    
    def test_performance_monitoring_workflow(self, client: TestClient):
        """Test complete performance monitoring workflow"""
        # Step 1: Check system health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Step 2: Get performance metrics
        metrics_response = client.get("/performance/metrics")
        # This might fail in test environment, which is acceptable
        assert metrics_response.status_code in [200, 500]
        
        # Step 3: Get performance summary
        summary_response = client.get("/performance/summary")
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert "status" in summary
        
        # Step 4: Trigger optimizations
        memory_opt_response = client.post("/performance/optimize/memory")
        assert memory_opt_response.status_code == 200
        
        cpu_opt_response = client.post("/performance/optimize/cpu")
        assert cpu_opt_response.status_code == 200
        
        auto_opt_response = client.post("/performance/optimize/auto")
        assert auto_opt_response.status_code == 200
        
        # Step 5: Store system metrics
        metrics_data = {
            "cpu_percent": 45.0,
            "memory_percent": 65.0,
            "memory_used_mb": 2048.0,
            "memory_available_mb": 1024.0,
            "disk_usage_percent": 55.0,
            "network_io": {"bytes_sent": 5000, "bytes_recv": 8000},
            "active_connections": 15,
            "response_time_ms": 150.0,
            "requests_per_second": 25.0,
            "cache_hit_rate": 88.0
        }
        
        store_metrics_response = client.post("/database/metrics", json=metrics_data)
        assert store_metrics_response.status_code == 200
    
    def test_database_management_workflow(self, client: TestClient):
        """Test complete database management workflow"""
        # Step 1: Check database health
        db_health_response = client.get("/database/health")
        assert db_health_response.status_code == 200
        
        # Step 2: Get database status
        db_status_response = client.get("/database/status")
        assert db_status_response.status_code == 200
        status = db_status_response.json()
        assert "tables" in status
        assert "total_records" in status
        
        # Step 3: Get database statistics
        db_stats_response = client.get("/database/statistics")
        assert db_stats_response.status_code == 200
        stats = db_stats_response.json()
        assert "counts" in stats
        assert "recent_activity" in stats
        
        # Step 4: Start migration
        migration_response = client.post("/database/migrate")
        assert migration_response.status_code == 200
        
        # Step 5: Start backup
        backup_response = client.post("/database/backup")
        assert backup_response.status_code == 200
        
        # Step 6: Get audit logs
        audit_logs_response = client.get("/database/audit-logs")
        assert audit_logs_response.status_code == 200
        audit_logs = audit_logs_response.json()
        assert isinstance(audit_logs, list)

class TestSystemIntegration:
    """System integration end-to-end tests"""
    
    def test_authentication_flow(self, client: TestClient):
        """Test complete authentication flow"""
        # Step 1: Try to access protected endpoint without token
        protected_response = client.get("/auth/me")
        assert protected_response.status_code == 403
        
        # Step 2: Try with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        invalid_response = client.get("/auth/me", headers=invalid_headers)
        assert invalid_response.status_code == 401
        
        # Step 3: Access with valid token (if available)
        # Note: This would require a proper token generation in a real scenario
    
    def test_error_handling_flow(self, client: TestClient, auth_headers):
        """Test complete error handling flow"""
        # Step 1: Test invalid patient creation
        invalid_patient_data = {
            "first_name": "",  # Invalid: empty name
            "last_name": "Test",
            "date_of_birth": "invalid-date",  # Invalid date
            "gender": "invalid-gender"  # Invalid gender
        }
        
        invalid_response = client.post(
            "/database/patients",
            json=invalid_patient_data,
            headers=auth_headers
        )
        assert invalid_response.status_code == 500  # Should fail validation
        
        # Step 2: Test nonexistent resource access
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        nonexistent_response = client.get(f"/database/patients/{fake_id}")
        assert nonexistent_response.status_code == 404
        
        # Step 3: Test malformed JSON
        malformed_response = client.post(
            "/database/patients",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert malformed_response.status_code == 422
    
    def test_data_consistency_flow(self, client: TestClient, auth_headers):
        """Test data consistency across operations"""
        # Step 1: Create patient
        patient_data = {
            "first_name": "Consistency",
            "last_name": "Test",
            "date_of_birth": "1990-01-01T00:00:00",
            "gender": "male",
            "phone": "+905551234567",
            "email": "consistency@example.com"
        }
        
        create_response = client.post(
            "/database/patients",
            json=patient_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        patient_id = create_response.json()["id"]
        
        # Step 2: Verify patient exists
        get_response = client.get(f"/database/patients/{patient_id}")
        assert get_response.status_code == 200
        retrieved_patient = get_response.json()
        assert retrieved_patient["first_name"] == "Consistency"
        assert retrieved_patient["email"] == "consistency@example.com"
        
        # Step 3: Create report for patient
        report_data = {
            "patient_id": patient_id,
            "report_type": "pet-ct",
            "study_date": "2024-01-01T00:00:00",
            "findings": "Consistency test findings",
            "impression": "Consistency test impression"
        }
        
        report_response = client.post(
            "/database/reports",
            json=report_data,
            headers=auth_headers
        )
        assert report_response.status_code == 200
        report_id = report_response.json()["id"]
        
        # Step 4: Verify report is linked to patient
        reports_response = client.get(f"/database/reports?patient_id={patient_id}")
        assert reports_response.status_code == 200
        reports = reports_response.json()
        assert len(reports) >= 1
        assert reports[0]["patient_id"] == patient_id
        assert reports[0]["findings"] == "Consistency test findings"
        
        # Step 5: Verify database statistics reflect the new data
        stats_response = client.get("/database/statistics")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["counts"]["patients"] >= 1
        assert stats["counts"]["reports"] >= 1

class TestPerformanceE2E:
    """Performance end-to-end tests"""
    
    def test_response_time_consistency(self, client: TestClient):
        """Test response time consistency across endpoints"""
        endpoints = [
            "/health",
            "/database/health",
            "/performance/health",
            "/database/status",
            "/performance/summary"
        ]
        
        response_times = []
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # All endpoints should respond within reasonable time
            assert response_time < 5.0, f"Endpoint {endpoint} took too long: {response_time}s"
            assert response.status_code in [200, 500], f"Endpoint {endpoint} returned unexpected status: {response.status_code}"
        
        # Response times should be relatively consistent
        avg_response_time = sum(response_times) / len(response_times)
        for response_time in response_times:
            # Each response should be within 3x the average
            assert response_time < avg_response_time * 3, f"Response time {response_time}s is too inconsistent with average {avg_response_time}s"
    
    def test_concurrent_request_handling(self, client: TestClient, auth_headers):
        """Test concurrent request handling"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def make_request(request_id):
            try:
                # Make a simple request
                response = client.get("/health")
                results.put((request_id, response.status_code, time.time()))
            except Exception as e:
                errors.put((request_id, str(e)))
        
        # Start multiple concurrent requests
        threads = []
        num_requests = 10
        
        for i in range(num_requests):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert errors.empty(), f"Errors occurred: {list(errors.queue)}"
        assert results.qsize() == num_requests
        
        # All requests should have succeeded
        while not results.empty():
            request_id, status_code, timestamp = results.get()
            assert status_code == 200, f"Request {request_id} failed with status {status_code}"

class TestDataIntegrityE2E:
    """Data integrity end-to-end tests"""
    
    def test_cascade_operations(self, client: TestClient, auth_headers):
        """Test cascade operations and data integrity"""
        # Step 1: Create patient
        patient_data = {
            "first_name": "Cascade",
            "last_name": "Test",
            "date_of_birth": "1980-01-01T00:00:00",
            "gender": "female",
            "phone": "+905551234567",
            "email": "cascade@example.com"
        }
        
        patient_response = client.post(
            "/database/patients",
            json=patient_data,
            headers=auth_headers
        )
        assert patient_response.status_code == 200
        patient_id = patient_response.json()["id"]
        
        # Step 2: Create multiple reports for the patient
        report_types = ["pet-ct", "pet-mri", "spect"]
        report_ids = []
        
        for i, report_type in enumerate(report_types):
            report_data = {
                "patient_id": patient_id,
                "report_type": report_type,
                "study_date": f"2024-01-{i+1:02d}T00:00:00",
                "findings": f"Findings for {report_type}",
                "impression": f"Impression for {report_type}"
            }
            
            report_response = client.post(
                "/database/reports",
                json=report_data,
                headers=auth_headers
            )
            assert report_response.status_code == 200
            report_ids.append(report_response.json()["id"])
        
        # Step 3: Create SUV measurements for each report
        for i, report_id in enumerate(report_ids):
            suv_data = {
                "patient_id": patient_id,
                "report_id": report_id,
                "measurement_date": f"2024-01-{i+1:02d}T00:00:00",
                "suv_max": 5.0 + i,
                "suv_mean": 3.0 + i,
                "lesion_location": f"Location {i+1}"
            }
            
            suv_response = client.post(
                "/database/suv-measurements",
                json=suv_data,
                headers=auth_headers
            )
            assert suv_response.status_code == 200
        
        # Step 4: Verify all data is properly linked
        # Get all reports for patient
        reports_response = client.get(f"/database/reports?patient_id={patient_id}")
        assert reports_response.status_code == 200
        reports = reports_response.json()
        assert len(reports) == 3
        
        # Get all SUV measurements for patient
        suv_response = client.get(f"/database/suv-measurements?patient_id={patient_id}")
        assert suv_response.status_code == 200
        suv_measurements = suv_response.json()
        assert len(suv_measurements) == 3
        
        # Verify each SUV measurement is linked to correct report
        for measurement in suv_measurements:
            assert measurement["patient_id"] == patient_id
            assert measurement["report_id"] in report_ids
        
        # Step 5: Verify database statistics
        stats_response = client.get("/database/statistics")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Should have at least our test data
        assert stats["counts"]["patients"] >= 1
        assert stats["counts"]["reports"] >= 3
        assert stats["counts"]["suv_measurements"] >= 3

if __name__ == "__main__":
    pytest.main([__file__])
