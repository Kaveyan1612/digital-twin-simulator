from pydantic import BaseModel
from typing import Dict, Any


class MotorParameters(BaseModel):
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
    pole_pairs: int = 2
    stator_resistance: float = 0.5
    torque_constant: float = 0.8
    back_emf_constant: float = 0.8


DEFAULT_PARAMETERS = MotorParameters()


def get_motor_parameters(motor_id: str = "MOTOR-001") -> MotorParameters:
    return MotorParameters(motor_id=motor_id)