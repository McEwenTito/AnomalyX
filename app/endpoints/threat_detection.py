from fastapi import APIRouter
from datetime import datetime
from app.models import LogPayload, ThreatDetectionResult

router = APIRouter()

# Dummy in-memory storage for logs and alerts
logs_db = []
alerts_db = []

@router.post("/detect-threat/", response_model=ThreatDetectionResult)
def detect_threat(payload: LogPayload):
    """
    Threat Detection Endpoint:
      - Receives log entries.
      - Applies dummy anomaly detection (to be replaced with Isolation Forest).
      - Returns a risk score and classification.
    """
    risk_score = 0.0
    classification = "normal"
    details = ""

    # Dummy logic for demonstration:
    for log in payload.logs:
        if log.status == 401 or "sql" in log.request.lower() or "drop" in log.request.lower():
            risk_score += 0.5
            classification = "potential threat"
            details += f"Suspicious activity detected from {log.source_ip}. "

    # Store logs for demo purposes
    logs_db.extend(payload.logs)

    # If threat detected, record an alert based on the first log entry
    if classification != "normal":
        alerts_db.append({
            "timestamp": datetime.now(),
            "source_ip": payload.logs[0].source_ip,
            "request": payload.logs[0].request,
            "risk_score": risk_score,
            "classification": classification
        })

    return ThreatDetectionResult(
        risk_score=risk_score,
        classification=classification,
        details=details.strip() if details else "No anomalies detected."
    )
