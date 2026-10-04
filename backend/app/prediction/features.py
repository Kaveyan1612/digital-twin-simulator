import numpy as np
from typing import List
from app.schemas.motor import MotorState


def extract_prediction_features(state: MotorState) -> np.ndarray:
    return np.array([
        state.speed / 5000.0,
        state.target_speed / 5000.0,
        state.load / 100.0,
        state.torque / 100.0,
        state.voltage / 500.0,
        state.current / 50.0,
        state.power / 20.0,
        state.temperature / 150.0,
        state.vibration / 10.0,
        state.efficiency,
        state.health_score / 100.0,
        1.0 if state.running else 0.0,
        abs(state.target_speed - state.speed) / 5000.0,
    ], dtype=np.float32)


def extract_sequence_features(states: List[MotorState], sequence_length: int = 10) -> np.ndarray:
    if len(states) < sequence_length:
        padding = [states[0]] * (sequence_length - len(states)) if states else [MotorState(
            timestamp=0, motor_id="", running=False, operating_mode="NORMAL",
            target_speed=0, speed=0, load=0, torque=0, voltage=0, current=0,
            power=0, temperature=25, vibration=0.5, efficiency=0, health_score=100,
            status="STOPPED", anomaly_detected=False, anomaly_type=None
        )] * sequence_length
        states = padding + list(states)
    
    states = states[-sequence_length:]
    return np.array([extract_prediction_features(s) for s in states], dtype=np.float32)


PREDICTION_FEATURE_NAMES = [
    "speed_norm",
    "target_speed_norm",
    "load_norm",
    "torque_norm",
    "voltage_norm",
    "current_norm",
    "power_norm",
    "temperature_norm",
    "vibration_norm",
    "efficiency",
    "health_score_norm",
    "running",
    "speed_deviation_norm",
]