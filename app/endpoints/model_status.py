from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/model-status/")
def model_status():
    """
    Model Status Endpoint:
      - Provides dummy status info for the AI model.
    """
    return {
        "model": "Isolation Forest",
        "status": "operational",
        "last_updated": datetime.now()
    }
