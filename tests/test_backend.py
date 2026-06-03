import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.database
import backend.models
from backend.main import app

try:
    import database
    import models
except ImportError:
    models = None

# Setup the in-memory database with StaticPool to share a single connection
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the shared in-memory database
backend.models.Base.metadata.create_all(bind=engine)
if models:
    models.Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply dependency overrides to all potential namespaces of get_db
app.dependency_overrides[backend.database.get_db] = override_get_db

try:
    app.dependency_overrides[database.get_db] = override_get_db
except NameError:
    pass

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Recreate tables before each test to ensure isolation on the static connection
    backend.models.Base.metadata.drop_all(bind=engine)
    backend.models.Base.metadata.create_all(bind=engine)
    if models:
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
    yield

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "CivicAssist AI Backend Running"}

def test_admin_health():
    response = client.get("/api/admin/health")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}

def test_dashboard_stats_empty():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    assert response.json() == {
        "total_complaints": 0,
        "resolved": 0,
        "pending": 0,
        "high_priority": 0
    }

def test_complaints_empty():
    response = client.get("/api/complaints/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_nonexistent_complaint():
    response = client.get("/api/complaints/nonexistent")
    assert response.status_code == 200
    assert response.json() == {"message": "Complaint not found"}

def test_update_status_nonexistent_complaint():
    response = client.put("/api/complaints/nonexistent/status", json={"status": "Resolved"})
    assert response.status_code == 200
    assert response.json() == {"message": "Complaint not found"}

def test_submit_complaint():
    payload = {
        "citizen_name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "complaint_text": "There is a huge pothole on Main Street.",
        "location": "Main Street",
        "latitude": 12.9716,
        "longitude": 77.5946
    }
    
    # Determine the actual import path used by fastapi for complaints router
    router_module = "routers.complaints" if "routers.complaints" in sys.modules else "backend.routers.complaints"
    
    with patch(f"{router_module}.classify", return_value="Pothole") as mock_classify, \
         patch(f"{router_module}.route", return_value={"department": "Road Operations Department", "email": "roads@example.com", "priority": "High"}) as mock_route, \
         patch(f"{router_module}.generate_letter", return_value="Mocked Letter Content") as mock_generate, \
         patch(f"{router_module}.create_pdf", return_value="/mock/path/complaint.pdf"):
         
        response = client.post("/api/complaints/", json=payload)
        
        assert response.status_code == 200
        res_data = response.json()
        assert "complaint_id" in res_data
        assert res_data["category"] == "Pothole"
        assert res_data["department"] == "Road Operations Department"
        assert res_data["priority"] == "High"
        assert res_data["generated_letter"] == "Mocked Letter Content"
        
        # Verify mock calls
        mock_classify.assert_called_once_with(payload["complaint_text"])
        mock_route.assert_called_once_with("Pothole")
        mock_generate.assert_called_once_with("Pothole", payload["location"], payload["complaint_text"])
        
        # Verify it was added to database
        complaint_id = res_data["complaint_id"]
        get_resp = client.get(f"/api/complaints/{complaint_id}")
        assert get_resp.status_code == 200
        complaint_data = get_resp.json()
        assert complaint_data["citizen_name"] == "John Doe"
        assert complaint_data["status"] == "Submitted"
        
        # Verify stats updated
        stats_resp = client.get("/api/dashboard/stats")
        assert stats_resp.json() == {
            "total_complaints": 1,
            "resolved": 0,
            "pending": 1,
            "high_priority": 1
        }
        
        # Test status update
        up_resp = client.put(f"/api/complaints/{complaint_id}/status", json={"status": "Resolved"})
        assert up_resp.status_code == 200
        assert up_resp.json()["new_status"] == "Resolved"
        
        # Verify stats updated to resolved
        stats_resp2 = client.get("/api/dashboard/stats")
        assert stats_resp2.json() == {
            "total_complaints": 1,
            "resolved": 1,
            "pending": 0,
            "high_priority": 1
        }
