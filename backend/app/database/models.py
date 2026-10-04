from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, Float, String, Integer, Text
from datetime import datetime
from typing import Optional
import sqlalchemy.dialects.sqlite as sqlite


class MotorState(SQLModel, table=True):
    __tablename__ = "motor_states"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, index=True))
    motor_id: str = Field(sa_column=Column(String(50), index=True))
    running: bool = False
    operating_mode: str = "NORMAL"
    target_speed: float = 0.0
    speed: float = 0.0
    load: float = 0.0
    torque: float = 0.0
    voltage: float = 0.0
    current: float = 0.0
    power: float = 0.0
    temperature: float = 0.0
    vibration: float = 0.0
    efficiency: float = 0.0
    health_score: float = 100.0
    status: str = "STOPPED"
    anomaly_detected: bool = False
    anomaly_type: Optional[str] = None


class Anomaly(SQLModel, table=True):
    __tablename__ = "anomalies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, index=True))
    motor_id: str = Field(sa_column=Column(String(50), index=True))
    anomaly_type: str = Field(sa_column=Column(String(100)))
    severity: str = Field(sa_column=Column(String(20)))
    confidence: float = 0.0
    description: str = Field(sa_column=Column(Text))
    parameter: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, index=True))
    motor_id: str = Field(sa_column=Column(String(50), index=True))
    alert_type: str = Field(sa_column=Column(String(50)))
    severity: str = Field(sa_column=Column(String(20)))
    title: str = Field(sa_column=Column(String(200)))
    message: str = Field(sa_column=Column(Text))
    parameter: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    acknowledged: bool = False


class Command(SQLModel, table=True):
    __tablename__ = "commands"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, index=True))
    motor_id: str = Field(sa_column=Column(String(50), index=True))
    command_type: str = Field(sa_column=Column(String(50)))
    parameters: str = Field(sa_column=Column(Text))
    executed: bool = True


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"
    model_config = {"protected_namespaces": ()}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, index=True))
    motor_id: str = Field(sa_column=Column(String(50), index=True))
    prediction_type: str = Field(sa_column=Column(String(50)))
    horizon_seconds: int = 0
    predicted_value: float = 0.0
    confidence: float = 0.0
    model_version: str = "1.0"


class SystemEvent(SQLModel, table=True):
    __tablename__ = "system_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime, index=True))
    motor_id: str = Field(sa_column=Column(String(50), index=True))
    event_type: str = Field(sa_column=Column(String(50)))
    description: str = Field(sa_column=Column(Text))
    details: Optional[str] = None