from fastapi import APIRouter
from app.models import LogPayload

router = APIRouter()

# We'll use the same logs_db from the threat_detection module in a real-world scenario.
# For this example, we are keeping logs in a separate variable.
logs_db = []

@router.get("/logs/")
def get_logs():
    """
    Logs Management Endpoint (GET):
      - Returns all stored logs.
    """
    return logs_db

@router.post("/logs/")
def add_logs(payload: LogPayload):
    """
    Logs Management Endpoint (POST):
      - Allows manual addition of log entries.
    """
    logs_db.extend(payload.logs)
    return {"message": "Logs added successfully", "count": len(payload.logs)}
