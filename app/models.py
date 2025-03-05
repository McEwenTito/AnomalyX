from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LogEntry(BaseModel):
    timestamp: datetime
    source_ip: str
    request: str
    status: int
    user_agent: str

class LogPayload(BaseModel):
    logs: List[LogEntry]

class ThreatDetectionResult(BaseModel):
    risk_score: float
    classification: str  # e.g., "normal" or "potential threat"
    details: Optional[str] = None

class Alert(BaseModel):
    timestamp: datetime
    source_ip: str
    request: str
    risk_score: float
    classification: str
