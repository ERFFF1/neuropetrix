from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    assert "version" in r.json()

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()
    assert r.json()["status"] == "healthy"















