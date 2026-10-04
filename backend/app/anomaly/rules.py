from typing import List, Dict, Any
from app.schemas.motor import MotorState, AnomalySeverity
from app.schemas.anomaly import AnomalyRule, AnomalyDetectionConfig
from app.core.config import settings
from app.core.logging import logger
import time


DEFAULT_RULES = [
    AnomalyRule(
        name="overtemperature_warning",
        parameter="temperature",
        condition=">",
        threshold=90.0,
        severity=AnomalySeverity.HIGH,
        description="Motor temperature exceeds warning threshold",
    ),
    AnomalyRule(
        name="overtemperature_critical",
        parameter="temperature",
        condition=">",
        threshold=110.0,
        severity=AnomalySeverity.CRITICAL,
        description="Motor temperature exceeds critical threshold",
    ),
    AnomalyRule(
        name="overcurrent_warning",
        parameter="current",
        condition=">",
        threshold=40.0,
        severity=AnomalySeverity.HIGH,
        description="Motor current exceeds warning threshold",
    ),
    AnomalyRule(
        name="overcurrent_critical",
        parameter="current",
        condition=">",
        threshold=50.0,
        severity=AnomalySeverity.CRITICAL,
        description="Motor current exceeds critical threshold",
    ),
    AnomalyRule(
        name="overspeed_warning",
        parameter="speed",
        condition=">",
        threshold=4500.0,
        severity=AnomalySeverity.HIGH,
        description="Motor speed exceeds warning threshold",
    ),
    AnomalyRule(
        name="overspeed_critical",
        parameter="speed",
        condition=">",
        threshold=5000.0,
        severity=AnomalySeverity.CRITICAL,
        description="Motor speed exceeds critical threshold",
    ),
    AnomalyRule(
        name="high_vibration_warning",
        parameter="vibration",
        condition=">",
        threshold=5.0,
        severity=AnomalySeverity.MEDIUM,
        description="Motor vibration exceeds warning threshold",
    ),
    AnomalyRule(
        name="high_vibration_critical",
        parameter="vibration",
        condition=">",
        threshold=8.0,
        severity=AnomalySeverity.CRITICAL,
        description="Motor vibration exceeds critical threshold",
    ),
    AnomalyRule(
        name="overload_warning",
        parameter="load",
        condition=">",
        threshold=90.0,
        severity=AnomalySeverity.MEDIUM,
        description="Motor load exceeds warning threshold",
    ),
    AnomalyRule(
        name="undervoltage_warning",
        parameter="voltage",
        condition="<",
        threshold=300.0,
        severity=AnomalySeverity.MEDIUM,
        description="Motor voltage below warning threshold",
    ),
    AnomalyRule(
        name="low_efficiency_warning",
        parameter="efficiency",
        condition="<",
        threshold=70.0,
        severity=AnomalySeverity.LOW,
        description="Motor efficiency below warning threshold",
    ),
    AnomalyRule(
        name="health_degraded",
        parameter="health_score",
        condition="<",
        threshold=50.0,
        severity=AnomalySeverity.HIGH,
        description="Motor health score degraded",
    ),
]


class RuleEngine:
    def __init__(self, config: AnomalyDetectionConfig = None):
        self.config = config or AnomalyDetectionConfig(rules=DEFAULT_RULES)
        self.speed_deviation_history: Dict[str, List[float]] = {}
        self.speed_deviation_window = 10
    
    def evaluate(self, state: MotorState) -> List[Dict[str, Any]]:
        anomalies = []
        
        for rule in self.config.rules:
            if not rule.enabled:
                continue
            
            value = getattr(state, rule.parameter, None)
            if value is None:
                continue
            
            triggered = False
            if rule.condition == ">":
                triggered = value > rule.threshold
            elif rule.condition == "<":
                triggered = value < rule.threshold
            elif rule.condition == ">=":
                triggered = value >= rule.threshold
            elif rule.condition == "<=":
                triggered = value <= rule.threshold
            elif rule.condition == "==":
                triggered = value == rule.threshold
            
            if triggered:
                anomalies.append({
                    "anomaly_type": rule.name.upper(),
                    "severity": rule.severity,
                    "confidence": 1.0,
                    "description": rule.description,
                    "parameter": rule.parameter,
                    "value": value,
                    "threshold": rule.threshold,
                })
        
        speed_deviation = abs(state.target_speed - state.speed)
        self._update_speed_deviation_history(state.motor_id, speed_deviation)
        if self._check_persistent_speed_deviation(state.motor_id):
            anomalies.append({
                "anomaly_type": "SPEED_DEVIATION_PERSISTENT",
                "severity": AnomalySeverity.MEDIUM,
                "confidence": 0.8,
                "description": "Speed deviation from target persists beyond threshold",
                "parameter": "speed_deviation",
                "value": speed_deviation,
                "threshold": 200.0,
            })
        
        return anomalies
    
    def _update_speed_deviation_history(self, motor_id: str, deviation: float):
        if motor_id not in self.speed_deviation_history:
            self.speed_deviation_history[motor_id] = []
        self.speed_deviation_history[motor_id].append(deviation)
        if len(self.speed_deviation_history[motor_id]) > self.speed_deviation_window:
            self.speed_deviation_history[motor_id].pop(0)
    
    def _check_persistent_speed_deviation(self, motor_id: str) -> bool:
        history = self.speed_deviation_history.get(motor_id, [])
        if len(history) < self.speed_deviation_window:
            return False
        return all(d > 200.0 for d in history)
    
    def add_rule(self, rule: AnomalyRule):
        self.config.rules.append(rule)
    
    def remove_rule(self, name: str):
        self.config.rules = [r for r in self.config.rules if r.name != name]
    
    def update_rule(self, name: str, **kwargs):
        for rule in self.config.rules:
            if rule.name == name:
                for key, value in kwargs.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                break


rule_engine = RuleEngine()