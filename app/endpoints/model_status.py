from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/model-status")
async def model_status():
    # Return a simple status object; you can add more details as needed.
    return {
        "model": "trained_model.pkl",
        "status": "operational",
        "last_updated": datetime.utcnow().isoformat()
    }
