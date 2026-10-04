from pydantic import BaseModel
from typing import List, Optional
from app.schemas.motor import PredictionResult


class PredictionConfig(BaseModel):
    enabled: bool = True
    horizon_seconds: int = 60
    update_interval: int = 10
    temperature_model: str = "linear"
    vibration_model: str = "linear"
    speed_model: str = "linear"
    health_model: str = "linear"


class PredictionForecast(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    prediction_type: str
    current_value: float
    predictions: List[PredictionResult]
    warning: Optional[str] = None
    warning_threshold: Optional[float] = None


class ModelMetrics(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    model_type: str
    mae: float
    rmse: float
    r2_score: float
    training_samples: int
    validation_samples: int
    last_trained: Optional[str] = None