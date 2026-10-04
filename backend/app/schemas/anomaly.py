from pydantic import BaseModel
from typing import List, Optional
from app.schemas.motor import AnomalySeverity


class AnomalyRule(BaseModel):
    name: str
    parameter: str
    condition: str
    threshold: float
    severity: AnomalySeverity
    description: str
    enabled: bool = True


class AnomalyDetectionConfig(BaseModel):
    rules: List[AnomalyRule] = []
    ml_enabled: bool = True
    ml_threshold: float = 0.5
    evaluation_window: int = 10


class AnomalySummary(BaseModel):
    total_anomalies: int
    by_severity: dict
    by_type: dict
    recent_anomalies: List[dict]