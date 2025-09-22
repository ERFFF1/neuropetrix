import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    """Health endpoint test"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "timestamp" in data
    assert "version" in data

def test_root():
    """Root endpoint test"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_health_legacy():
    """Legacy health endpoint test"""
    response = client.get("/health/legacy")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"












