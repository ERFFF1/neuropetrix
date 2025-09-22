import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.report import ReportRequest, ReportType, Patient

client = TestClient(app)

def test_report_minimal():
    """Minimal report request test"""
    req = ReportRequest(
        patient=Patient(hasta_no="001", ad_soyad="Test Hasta"),
        report_type=ReportType(standard=True)
    )
    assert req.patient.hasta_no == "001"
    assert req.patient.ad_soyad == "Test Hasta"
    assert req.report_type.standard == True
    assert req.report_type.tsnm == False

def test_report_tsnm():
    """TSNM report request test"""
    req = ReportRequest(
        patient=Patient(hasta_no="002", ad_soyad="TSNM Test"),
        report_type=ReportType(tsnm=True, standard=False)
    )
    assert req.report_type.tsnm == True
    assert req.report_type.standard == False

def test_report_dicom_ai():
    """DICOM AI report request test"""
    req = ReportRequest(
        patient=Patient(hasta_no="003", ad_soyad="DICOM Test"),
        report_type=ReportType(dicom_ai=True, standard=False)
    )
    assert req.report_type.dicom_ai == True
    assert req.report_type.standard == False

def test_report_templates():
    """Report templates endpoint test"""
    response = client.get("/reports/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) > 0













