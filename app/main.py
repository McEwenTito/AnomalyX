from fastapi import FastAPI
from app.endpoints import health, model_status, threat_detection, logs, alerts

app = FastAPI(title="AI Cybersecurity API")

app.include_router(health.router, prefix="/api")
app.include_router(model_status.router, prefix="/api")
app.include_router(threat_detection.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Cybersecurity API!"}

# Run with: uvicorn app.main:app --reload
