from typing import Dict
from app.schemas.motor import MotorState, AnomalySeverity
from app.core.logging import logger


class HealthService:
    def calculate_health_score(self, state: MotorState) -> Dict[str, float]:
        temp_factor = max(0, 100 - (state.temperature / 120.0) * 100)
        vib_factor = max(0, 100 - (state.vibration / 10.0) * 100)
        current_factor = max(0, 100 - (state.current / 50.0) * 100)
        speed_dev = abs(state.target_speed - state.speed) / max(state.target_speed, 1)
        speed_factor = max(0, 100 - speed_dev * 100)
        load_factor = max(0, 100 - (state.load / 100.0) * 30)
        eff_factor = state.efficiency * 100
        fault_factor = 0 if state.anomaly_detected else 100
        
        weights = [0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]
        factors = [temp_factor, vib_factor, current_factor, speed_factor, load_factor, eff_factor, fault_factor]
        
        score = sum(w * f for w, f in zip(weights, factors))
        score = max(0, min(100, score))
        
        return {
            "score": round(score, 1),
            "temperature_factor": round(temp_factor, 1),
            "vibration_factor": round(vib_factor, 1),
            "current_factor": round(current_factor, 1),
            "speed_deviation_factor": round(speed_factor, 1),
            "load_factor": round(load_factor, 1),
            "efficiency_factor": round(eff_factor, 1),
            "fault_factor": round(fault_factor, 1),
        }
    
    def get_health_status(self, score: float) -> str:
        if score >= 90:
            return "HEALTHY"
        elif score >= 75:
            return "GOOD"
        elif score >= 50:
            return "WARNING"
        elif score >= 25:
            return "CRITICAL"
        else:
            return "FAILURE"
    
    def get_health_color(self, score: float) -> str:
        if score >= 90:
            return "#00C851"
        elif score >= 75:
            return "#8BC34A"
        elif score >= 50:
            return "#FF8800"
        elif score >= 25:
            return "#FF4444"
        else:
            return "#8B0000"


health_service = HealthService()