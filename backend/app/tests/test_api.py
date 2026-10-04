import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Digital Twin Simulator"
    assert "websocket" in data


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "simulation_running" in data
    assert "database" in data


def test_twin_state_endpoint(client):
    response = client.get("/api/twin/state")
    assert response.status_code == 200
    data = response.json()
    assert "motor_id" in data
    assert "running" in data
    assert "speed" in data
    assert "temperature" in data


def test_twin_config_endpoint(client):
    response = client.get("/api/twin/config")
    assert response.status_code == 200
    data = response.json()
    assert "motor_id" in data
    assert "max_speed" in data
    assert "max_temperature" in data


def test_start_motor_endpoint(client):
    response = client.post("/api/twin/start")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_stop_motor_endpoint(client):
    response = client.post("/api/twin/stop")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_reset_motor_endpoint(client):
    response = client.post("/api/twin/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_emergency_stop_endpoint(client):
    response = client.post("/api/twin/emergency-stop")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_set_target_speed_endpoint(client):
    response = client.post("/api/twin/target-speed", json={"value": 3000})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_set_target_speed_invalid(client):
    response = client.post("/api/twin/target-speed", json={"value": -100})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_set_load_endpoint(client):
    response = client.post("/api/twin/load", json={"value": 50})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_set_voltage_endpoint(client):
    response = client.post("/api/twin/voltage", json={"value": 415})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_set_operating_mode_endpoint(client):
    response = client.post("/api/twin/operating-mode", json={"value": "HIGH_LOAD"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_set_invalid_operating_mode(client):
    response = client.post("/api/twin/operating-mode", json={"value": "INVALID"})
    assert response.status_code == 400


def test_inject_fault_endpoint(client):
    response = client.post("/api/twin/inject-fault", json={"fault": "overtemperature", "value": 1.0})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_inject_invalid_fault(client):
    response = client.post("/api/twin/inject-fault", json={"fault": "invalid_fault"})
    assert response.status_code == 400


def test_clear_fault_endpoint(client):
    response = client.post("/api/twin/clear-fault")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_history_endpoint(client):
    response = client.get("/api/twin/history?hours=1&limit=100")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_statistics_endpoint(client):
    response = client.get("/api/twin/statistics?hours=1")
    assert response.status_code == 200
    data = response.json()
    assert "avg_speed" in data
    assert "max_temperature" in data
    assert "anomaly_count" in data


def test_docs_endpoint(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()