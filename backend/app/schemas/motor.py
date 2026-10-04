from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class OperatingMode(str, Enum):
    NORMAL = "NORMAL"
    HIGH_LOAD = "HIGH_LOAD"
    COOLING = "COOLING"
    MAINTENANCE = "MAINTENANCE"
    FAULT_TEST = "FAULT_TEST"


class MotorStatus(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    FAULT = "FAULT"
    MAINTENANCE = "MAINTENANCE"


class AnomalySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FaultType(str, Enum):
    OVERTEMPERATURE = "overtemperature"
    OVERCURRENT = "overcurrent"
    HIGH_VIBRATION = "high_vibration"
    OVERSPEED = "overspeed"
    UNDERVOLTAGE = "undervoltage"
    OVERLOAD = "overload"
    SENSOR_ANOMALY = "sensor_anomaly"
    COMBINED = "combined"


class MotorState(BaseModel):
    timestamp: float
    motor_id: str
    running: bool
    operating_mode: OperatingMode
    target_speed: float
    speed: float
    load: float
    torque: float
    voltage: float
    current: float
    power: float
    temperature: float
    vibration: float
    efficiency: float
    health_score: float
    status: MotorStatus
    anomaly_detected: bool
    anomaly_type: Optional[str] = None
    anomaly_severity: Optional[AnomalySeverity] = None


class MotorConfig(BaseModel):
    motor_id: str = "MOTOR-001"
    max_speed: float = 5000.0
    max_temperature: float = 120.0
    max_current: float = 50.0
    max_vibration: float = 10.0
    max_load: float = 100.0
    max_voltage: float = 500.0
    rated_power: float = 15.0
    rated_torque: float = 50.0
    rated_speed: float = 3000.0
    rated_current: float = 25.0
    rated_voltage: float = 415.0
    inertia: float = 0.1
    thermal_resistance: float = 0.5
    thermal_capacitance: float = 100.0
    cooling_coefficient: float = 0.1
    friction_coefficient: float = 0.02
    efficiency_base: float = 0.95


class AnomalyResult(BaseModel):
    anomaly_detected: bool
    severity: AnomalySeverity = AnomalySeverity.INFO
    anomaly_type: Optional[str] = None
    confidence: float = 0.0
    timestamp: float
    description: str = ""
    parameter: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None


class PredictionResult(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    prediction_type: str
    horizon_seconds: int
    predicted_value: float
    confidence: float
    timestamp: float
    model_version: str = "1.0"


class HealthScore(BaseModel):
    score: float
    temperature_factor: float
    vibration_factor: float
    current_factor: float
    speed_deviation_factor: float
    load_factor: float
    efficiency_factor: float
    fault_factor: float


class AlertInfo(BaseModel):
    id: Optional[int] = None
    timestamp: float
    alert_type: str
    severity: AnomalySeverity
    title: str
    message: str
    parameter: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    acknowledged: bool = False


class CommandRequest(BaseModel):
    type: str
    value: Optional[float] = None
    fault: Optional[FaultType] = None


class CommandResponse(BaseModel):
    success: bool
    message: str
    command_id: Optional[int] = None


class HistoricalDataPoint(BaseModel):
    timestamp: float
    speed: float
    target_speed: float
    load: float
    torque: float
    voltage: float
    current: float
    power: float
    temperature: float
    vibration: float
    efficiency: float
    health_score: float


class StatisticsResponse(BaseModel):
    avg_speed: float
    max_speed: float
    avg_temperature: float
    max_temperature: float
    avg_load: float
    avg_current: float
    avg_power: float
    avg_efficiency: float
    avg_vibration: float
    min_health_score: float
    data_points: int
    anomaly_count: int
    critical_fault_count: int
    uptime_seconds: float


class HealthResponse(BaseModel):
    status: str
    simulation_running: bool
    database: str
    websocket_clients: int
    uptime_seconds: float