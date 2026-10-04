from pydantic import BaseModel
from typing import Optional
from enum import Enum
from dataclasses import dataclass, field


class FaultType(str, Enum):
    OVERTEMPERATURE = "overtemperature"
    OVERCURRENT = "overcurrent"
    HIGH_VIBRATION = "high_vibration"
    OVERSPEED = "overspeed"
    UNDERVOLTAGE = "undervoltage"
    OVERLOAD = "overload"
    SENSOR_ANOMALY = "sensor_anomaly"
    COMBINED = "combined"


class FaultState(BaseModel):
    active: bool = False
    fault_type: Optional[FaultType] = None
    intensity: float = 0.0
    start_time: Optional[float] = None
    target_value: Optional[float] = None
    progression_rate: float = 1.0


class FaultInjection(BaseModel):
    fault_type: FaultType
    intensity: float = 1.0
    duration: Optional[float] = None


FAULT_PROFILES = {
    FaultType.OVERTEMPERATURE: {
        "temperature_multiplier": 2.5,
        "progression_rate": 0.5,
        "affects": ["temperature", "efficiency", "vibration"],
    },
    FaultType.OVERCURRENT: {
        "current_multiplier": 2.0,
        "progression_rate": 1.0,
        "affects": ["current", "temperature", "torque"],
    },
    FaultType.HIGH_VIBRATION: {
        "vibration_multiplier": 5.0,
        "progression_rate": 0.8,
        "affects": ["vibration", "health_score"],
    },
    FaultType.OVERSPEED: {
        "speed_multiplier": 1.3,
        "progression_rate": 2.0,
        "affects": ["speed", "vibration", "current"],
    },
    FaultType.UNDERVOLTAGE: {
        "voltage_multiplier": 0.7,
        "progression_rate": 1.0,
        "affects": ["voltage", "current", "torque", "speed"],
    },
    FaultType.OVERLOAD: {
        "load_multiplier": 1.5,
        "progression_rate": 0.5,
        "affects": ["load", "torque", "current", "temperature"],
    },
    FaultType.SENSOR_ANOMALY: {
        "noise_multiplier": 10.0,
        "progression_rate": 1.0,
        "affects": ["all"],
    },
    FaultType.COMBINED: {
        "temperature_multiplier": 2.0,
        "current_multiplier": 1.5,
        "vibration_multiplier": 3.0,
        "progression_rate": 0.5,
        "affects": ["all"],
    },
}


def get_fault_profile(fault_type: FaultType) -> dict:
    return FAULT_PROFILES.get(fault_type, {})