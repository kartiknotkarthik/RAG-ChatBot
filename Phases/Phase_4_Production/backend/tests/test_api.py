import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

# Create a TestClient for FastAPI
client = TestClient(app)

def test_health_check_endpoint():
    # Verify the backend is online and healthy
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_factual_query_flow():
    # Test if the factual query response matches the Pydantic schema
    payload = {"query": "What is HDFC expense ratio?"}
    response = client.post("/query", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "source" in data
    assert data["is_advice"] == False

def test_advice_guardrail_trigger():
    # Test if the advice detection correctly triggers the refusal response
    payload = {"query": "Should I buy SBI Gold?"}
    response = client.post("/query", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "I apologize" in data["answer"]
    assert "consult a SEBI-registered advisor" in data["answer"]
    assert data["is_advice"] == True

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__]))
