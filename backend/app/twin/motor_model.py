import numpy as np
from typing import Optional
from app.twin.parameters import MotorParameters, DEFAULT_PARAMETERS
from app.twin.faults import FaultState, FaultType, FAULT_PROFILES
from app.core.config import settings
from app.core.logging import logger
import time


class MotorModel:
    def __init__(self, params: MotorParameters = None):
        self.params = params or DEFAULT_PARAMETERS
        self.reset()
    
    def reset(self):
        self.speed = 0.0
        self.target_speed = 0.0
        self.load = 0.0
        self.torque = 0.0
        self.voltage = 0.0
        self.current = 0.0
        self.power = 0.0
        self.temperature = 25.0
        self.vibration = 0.5
        self.efficiency = self.params.efficiency_base
        self.health_score = 100.0
        self.running = False
        self.operating_mode = "NORMAL"
        self.status = "STOPPED"
        self.fault_state = FaultState()
        self.last_update = time.time()
        self.anomaly_detected = False
        self.anomaly_type = None
        self.anomaly_severity = "INFO"
    
    def set_fault(self, fault_type: FaultType, intensity: float = 1.0):
        self.fault_state = FaultState(
            active=True,
            fault_type=fault_type,
            intensity=min(max(intensity, 0.0), 1.0),
            start_time=time.time(),
            progression_rate=FAULT_PROFILES.get(fault_type, {}).get("progression_rate", 1.0)
        )
        logger.info(f"Fault injected: {fault_type.value} with intensity {intensity}")
    
    def clear_fault(self):
        self.fault_state = FaultState()
        logger.info("Fault cleared")
    
    def apply_fault_effects(self, dt: float):
        if not self.fault_state.active or self.fault_state.fault_type is None:
            return
        
        profile = FAULT_PROFILES.get(self.fault_state.fault_type, {})
        progression = self.fault_state.progression_rate * self.fault_state.intensity * dt
        
        if self.fault_state.fault_type == FaultType.OVERTEMPERATURE:
            multiplier = profile.get("temperature_multiplier", 2.0)
            self.temperature += progression * multiplier * 10
        
        elif self.fault_state.fault_type == FaultType.OVERCURRENT:
            multiplier = profile.get("current_multiplier", 2.0)
            self.current *= multiplier
            self.temperature += progression * 5
        
        elif self.fault_state.fault_type == FaultType.HIGH_VIBRATION:
            multiplier = profile.get("vibration_multiplier", 5.0)
            self.vibration = profile.get("vibration_multiplier", 5.0) + np.random.normal(0, 0.5)
        
        elif self.fault_state.fault_type == FaultType.OVERSPEED:
            multiplier = profile.get("speed_multiplier", 1.3)
            self.target_speed = min(self.target_speed * multiplier, self.params.max_speed * 1.2)
        
        elif self.fault_state.fault_type == FaultType.UNDERVOLTAGE:
            multiplier = profile.get("voltage_multiplier", 0.7)
            self.voltage *= multiplier
        
        elif self.fault_state.fault_type == FaultType.OVERLOAD:
            multiplier = profile.get("load_multiplier", 1.5)
            self.load = min(self.load * multiplier, self.params.max_load)
        
        elif self.fault_state.fault_type == FaultType.COMBINED:
            self.temperature += progression * 15
            self.current *= 1.3
            self.vibration = 3.0 + np.random.normal(0, 0.3)
    
    def update(self, dt: float, target_speed: float = None, load: float = None, voltage: float = None):
        if target_speed is not None:
            self.target_speed = np.clip(target_speed, 0, self.params.max_speed)
        
        if load is not None:
            self.load = np.clip(load, 0, self.params.max_load)
        
        if voltage is not None:
            self.voltage = np.clip(voltage, 0, self.params.max_voltage)
        
        if not self.running:
            self._update_stopped(dt)
            return
        
        self._update_running(dt)
        self.apply_fault_effects(dt)
        self._add_noise()
        self._clamp_values()
    
    def _update_stopped(self, dt: float):
        if self.speed > 0:
            deceleration = self.params.friction_coefficient * self.speed * dt
            self.speed = max(0, self.speed - deceleration)
        
        if self.temperature > 25:
            cooling = self.params.cooling_coefficient * (self.temperature - 25) * dt
            self.temperature = max(25, self.temperature - cooling)
        
        self.torque = 0
        self.current = 0
        self.power = 0
        self.vibration = max(0.1, self.vibration - 0.1 * dt)
        self.efficiency = 0
        self.status = "STOPPED"
    
    def _update_running(self, dt: float):
        speed_error = self.target_speed - self.speed
        acceleration = speed_error * 0.5 * dt
        max_accel = self.params.max_speed / (self.params.inertia * 10)
        acceleration = np.clip(acceleration, -max_accel, max_accel)
        self.speed += acceleration
        
        load_factor = self.load / 100.0
        self.torque = self.params.rated_torque * load_factor * (self.speed / self.params.rated_speed)
        
        if self.voltage > 0:
            back_emf = self.params.back_emf_constant * self.speed / 1000.0
            effective_voltage = max(0, self.voltage - back_emf)
            self.current = effective_voltage / self.params.stator_resistance * load_factor
        else:
            self.current = 0
        
        self.current = min(self.current, self.params.max_current * 1.2)
        
        mechanical_power = self.torque * self.speed * 2 * np.pi / 60000.0
        electrical_power = self.voltage * self.current * np.sqrt(3) / 1000.0
        self.power = mechanical_power
        
        if electrical_power > 0:
            self.efficiency = min(0.98, mechanical_power / electrical_power)
        else:
            self.efficiency = 0
        
        self._update_temperature(dt)
        self._update_vibration(dt)
        self._update_health_score()
        self.status = "RUNNING"
    
    def _update_temperature(self, dt: float):
        heat_generated = self.current ** 2 * self.params.stator_resistance * dt * 0.1
        cooling = self.params.cooling_coefficient * (self.temperature - 25) * dt
        self.temperature += heat_generated - cooling
        self.temperature = max(25, self.temperature)
    
    def _update_vibration(self, dt: float):
        base_vibration = 0.5 + (self.speed / self.params.max_speed) * 1.0
        load_vibration = (self.load / 100.0) * 1.5
        temp_vibration = max(0, (self.temperature - 80) / 100.0) * 2.0
        self.vibration = base_vibration + load_vibration + temp_vibration + np.random.normal(0, 0.1)
        self.vibration = max(0.1, self.vibration)
    
    def _update_health_score(self):
        temp_factor = max(0, 100 - (self.temperature / self.params.max_temperature) * 100)
        vib_factor = max(0, 100 - (self.vibration / self.params.max_vibration) * 100)
        current_factor = max(0, 100 - (self.current / self.params.max_current) * 100)
        speed_dev = abs(self.speed - self.target_speed) / max(self.target_speed, 1)
        speed_factor = max(0, 100 - speed_dev * 100)
        load_factor = max(0, 100 - (self.load / 100.0) * 30)
        eff_factor = self.efficiency * 100
        fault_factor = 0 if self.fault_state.active else 100
        
        weights = [0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]
        factors = [temp_factor, vib_factor, current_factor, speed_factor, load_factor, eff_factor, fault_factor]
        
        self.health_score = sum(w * f for w, f in zip(weights, factors))
        self.health_score = np.clip(self.health_score, 0, 100)
    
    def _add_noise(self):
        self.speed += np.random.normal(0, 0.5)
        self.torque += np.random.normal(0, 0.1)
        self.current += np.random.normal(0, 0.05)
        self.temperature += np.random.normal(0, 0.1)
        self.vibration += np.random.normal(0, 0.02)
    
    def _clamp_values(self):
        self.speed = np.clip(self.speed, 0, self.params.max_speed * 1.1)
        self.torque = np.clip(self.torque, 0, self.params.rated_torque * 2)
        self.current = np.clip(self.current, 0, self.params.max_current * 1.5)
        self.voltage = np.clip(self.voltage, 0, self.params.max_voltage)
        self.power = max(0, self.power)
        self.temperature = np.clip(self.temperature, 25, self.params.max_temperature * 1.5)
        self.vibration = np.clip(self.vibration, 0.1, self.params.max_vibration * 2)
        self.efficiency = np.clip(self.efficiency, 0, 0.98)
        self.health_score = np.clip(self.health_score, 0, 100)
        self.load = np.clip(self.load, 0, self.params.max_load)
    
    def start(self):
        if not self.running:
            self.running = True
            self.status = "STARTING"
            self.voltage = self.params.rated_voltage
            logger.info("Motor started")
    
    def stop(self):
        if self.running:
            self.running = False
            self.target_speed = 0
            self.status = "STOPPING"
            logger.info("Motor stop requested")
    
    def emergency_stop(self):
        self.running = False
        self.target_speed = 0
        self.load = 0
        self.status = "EMERGENCY_STOP"
        logger.warning("EMERGENCY STOP activated")
    
    def get_state_dict(self) -> dict:
        return {
            "timestamp": time.time(),
            "motor_id": self.params.motor_id,
            "running": self.running,
            "operating_mode": self.operating_mode,
            "target_speed": round(self.target_speed, 1),
            "speed": round(self.speed, 1),
            "load": round(self.load, 1),
            "torque": round(self.torque, 1),
            "voltage": round(self.voltage, 1),
            "current": round(self.current, 1),
            "power": round(self.power, 2),
            "temperature": round(self.temperature, 1),
            "vibration": round(self.vibration, 2),
            "efficiency": round(self.efficiency * 100, 1),
            "health_score": round(self.health_score, 1),
            "status": self.status,
            "anomaly_detected": self.anomaly_detected,
            "anomaly_type": self.anomaly_type,
        }