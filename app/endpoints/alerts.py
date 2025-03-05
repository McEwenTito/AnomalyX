from fastapi import APIRouter

router = APIRouter()

# In a real scenario, you'd share the alerts_db from threat_detection.
alerts_db = []

@router.get("/alerts/")
def get_alerts():
    """
    Alerts Endpoint:
      - Returns a list of detected threat alerts.
    """
    return alerts_db
