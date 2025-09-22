"""
Test Configuration
Test konfigürasyonu ve fixtures
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main_working import app
from backend.core.database import Base, get_db, get_async_db
from backend.core.auth import create_access_token

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_async_db():
    # Mock async session for testing
    pass

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_async_db] = override_get_async_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):
    """Test client"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    token = create_access_token(data={"sub": "testuser", "roles": ["admin"]})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1990-01-01T00:00:00",
        "gender": "male",
        "phone": "+905551234567",
        "email": "test@example.com",
        "address": "Test Address",
        "medical_history": "No known medical history",
        "allergies": ["penicillin"],
        "emergency_contact": {
            "name": "Emergency Contact",
            "phone": "+905559876543",
            "relationship": "spouse"
        }
    }

@pytest.fixture
def sample_report_data():
    """Sample report data for testing"""
    return {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "report_type": "pet-ct",
        "study_date": "2024-01-01T00:00:00",
        "findings": "Test findings",
        "impression": "Test impression",
        "recommendations": "Test recommendations",
        "attachments": [],
        "status": "draft"
    }

@pytest.fixture
def sample_suv_data():
    """Sample SUV measurement data for testing"""
    return {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "report_id": "123e4567-e89b-12d3-a456-426614174001",
        "measurement_date": "2024-01-01T00:00:00",
        "suv_max": 8.5,
        "suv_mean": 4.2,
        "suv_peak": 7.8,
        "lesion_location": "Liver",
        "lesion_size": 2.5,
        "notes": "Test SUV measurement"
    }
