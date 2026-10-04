from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./digital_twin.db"
    simulation_frequency: int = 10
    websocket_update_rate: int = 5
    max_speed: float = 5000.0
    max_temperature: float = 120.0
    max_current: float = 50.0
    max_vibration: float = 10.0
    max_load: float = 100.0
    max_voltage: float = 500.0
    motor_id: str = "MOTOR-001"
    anomaly_detection_enabled: bool = True
    ml_anomaly_detection_enabled: bool = True
    prediction_enabled: bool = True
    live_history_points: int = 1000
    database_retention_days: int = 30
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()