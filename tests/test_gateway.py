import os
os.environ.setdefault("EDGE_API_KEY", "test-key")

from fastapi.testclient import TestClient
from gateway import app as gateway

client = TestClient(gateway.app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert "configured_nodes" in response.json()

def test_auth_required():
    assert client.get("/v1/nodes").status_code == 401

def test_invalid_task():
    response = client.post(
        "/v1/tasks",
        headers={"Authorization": "Bearer test-key"},
        json={"task": "unsupported", "input": "hello"},
    )
    assert response.status_code == 422

def test_unconfigured_nodes():
    original = gateway.nodes
    try:
        gateway.nodes = []
        response = client.post(
            "/v1/tasks",
            headers={"Authorization": "Bearer test-key"},
            json={"task": "general", "input": "hello"},
        )
        assert response.status_code == 503
    finally:
        gateway.nodes = original

def test_mixed_device_registration(monkeypatch):
    monkeypatch.setenv("NODE_1_PLATFORM", "android")
    monkeypatch.setenv("NODE_1_URL", "http://127.0.0.1:8101")
    monkeypatch.setenv("NODE_1_KEY", "a")
    monkeypatch.setenv("NODE_2_PLATFORM", "ios")
    monkeypatch.setenv("NODE_2_URL", "http://127.0.0.1:8102")
    monkeypatch.setenv("NODE_2_KEY", "b")
    monkeypatch.setenv("NODE_3_PLATFORM", "windows")
    monkeypatch.setenv("NODE_3_URL", "http://127.0.0.1:8103")
    monkeypatch.setenv("NODE_3_KEY", "c")
    monkeypatch.setenv("NODE_4_PLATFORM", "macos")
    monkeypatch.setenv("NODE_4_URL", "http://127.0.0.1:8104")
    monkeypatch.setenv("NODE_4_KEY", "d")
    nodes = gateway.load_nodes()
    assert len(nodes) == 4
    assert [n.platform for n in nodes] == ["android", "ios", "windows", "macos"]
