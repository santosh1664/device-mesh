import os
os.environ.setdefault("EDGE_API_KEY", "test-key")
from fastapi.testclient import TestClient
from gateway.app import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_auth_required():
    assert client.get("/v1/nodes").status_code == 401

def test_invalid_task():
    response = client.post("/v1/tasks", headers={"Authorization": "Bearer test-key"}, json={"task": "unsupported", "input": "hello"})
    assert response.status_code == 422

def test_unconfigured_nodes():
    response = client.post("/v1/tasks", headers={"Authorization": "Bearer test-key"}, json={"task": "general", "input": "hello"})
    assert response.status_code == 503
