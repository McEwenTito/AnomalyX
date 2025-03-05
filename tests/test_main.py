from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_detect_threat_normal():
    payload = {
        "logs": [
            {
                "timestamp": "2025-03-04T12:34:56Z",
                "source_ip": "192.168.1.100",
                "request": "/home",
                "status": 200,
                "user_agent": "Mozilla/5.0"
            }
        ]
    }
    response = client.post("/api/detect-threat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect a normal classification since there are no suspicious patterns.
    assert data["classification"] == "normal"
    assert "No anomalies detected." in data["details"]

def test_detect_threat_suspicious():
    payload = {
        "logs": [
            {
                "timestamp": "2025-03-04T12:34:56Z",
                "source_ip": "10.0.0.1",
                "request": "SELECT * FROM users WHERE username='admin' OR '1'='1'",
                "status": 401,
                "user_agent": "Mozilla/5.0"
            }
        ]
    }
    response = client.post("/api/detect-threat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Expect the log to be flagged as a potential threat.
    assert data["classification"] == "potential threat"
    assert data["risk_score"] > 0

def test_logs_post_and_get():
    payload = {
        "logs": [
            {
                "timestamp": "2025-03-04T12:00:00Z",
                "source_ip": "192.168.1.101",
                "request": "/login",
                "status": 401,
                "user_agent": "Mozilla/5.0"
            }
        ]
    }
    post_response = client.post("/api/logs/", json=payload)
    assert post_response.status_code == 200
    post_data = post_response.json()
    assert post_data["message"] == "Logs added successfully"
    # Now retrieve the logs
    get_response = client.get("/api/logs/")
    assert get_response.status_code == 200
    logs = get_response.json()
    # Check that our test log is present.
    assert any(log["source_ip"] == "192.168.1.101" for log in logs)

def test_alerts():
    # Submit a suspicious log to trigger an alert
    payload = {
        "logs": [
            {
                "timestamp": "2025-03-04T12:45:00Z",
                "source_ip": "192.168.1.102",
                "request": "DROP TABLE users;",
                "status": 401,
                "user_agent": "Mozilla/5.0"
            }
        ]
    }
    client.post("/api/detect-threat/", json=payload)
    alerts_response = client.get("/api/alerts/")
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()
    # Verify that at least one alert matches our submitted suspicious log.
    assert any(alert["source_ip"] == "192.168.1.102" for alert in alerts)

def test_model_status():
    response = client.get("/api/model-status/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("model") == "Isolation Forest"
    assert data.get("status") == "operational"
    assert "last_updated" in data
    assert datetime.fromisoformat(data["last_updated"]) <= datetime.now()