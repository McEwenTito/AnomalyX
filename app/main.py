from fastapi import FastAPI
from app.endpoints import health, threat_detection, logs, alerts, model_status

app = FastAPI()

# Include endpoints from our endpoints package
app.include_router(health.router, prefix="/api")
app.include_router(threat_detection.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(model_status.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
