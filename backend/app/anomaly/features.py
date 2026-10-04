import numpy as np
from typing import List, Dict, Any
from app.schemas.motor import MotorState
from app.core.logging import logger


def extract_features(state: MotorState) -> np.ndarray:
    features = np.array([
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
        state.temperature * state.current / (150.0 * 50.0),
        state.vibration * state.load / (10.0 * 100.0),
    ], dtype=np.float32)
    
    return features


def extract_features_batch(states: List[MotorState]) -> np.ndarray:
    return np.array([extract_features(s) for s in states], dtype=np.float32)


FEATURE_NAMES = [
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
    "temp_current_interaction",
    "vib_load_interaction",
]


def get_feature_names() -> List[str]:
    return FEATURE_NAMES.copy()


def normalize_features(features: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (features - mean) / (std + 1e-8)


def denormalize_features(features: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return features * std + mean