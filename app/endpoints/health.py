from fastapi import APIRouter

router = APIRouter()

@router.get("/health/")
def health_check():
    """
    Health Check Endpoint: Returns API status.
    """
    return {"status": "ok"}
