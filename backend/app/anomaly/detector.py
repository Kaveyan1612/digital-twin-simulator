from typing import List, Dict, Any, Optional
from app.schemas.motor import MotorState, AnomalySeverity
from app.schemas.anomaly import AnomalyDetectionConfig
from app.anomaly.rules import RuleEngine, rule_engine, DEFAULT_RULES
from app.anomaly.model import MLAnomalyDetector, ml_anomaly_detector
from app.anomaly.features import extract_features
from app.core.config import settings
from app.core.logging import logger
import time


class AnomalyDetector:
    def __init__(self, config: AnomalyDetectionConfig = None):
        self.config = config or AnomalyDetectionConfig()
        self.rule_engine = rule_engine
        self.ml_detector = ml_anomaly_detector
        self.last_anomaly_time = 0
        self.anomaly_cooldown = 5.0
    
    def detect(self, state: MotorState) -> List[Dict[str, Any]]:
        all_anomalies = []
        
        if settings.anomaly_detection_enabled:
            rule_anomalies = self.rule_engine.evaluate(state)
            all_anomalies.extend(rule_anomalies)
        
        if settings.ml_anomaly_detection_enabled and self.ml_detector.trained:
            ml_anomaly, confidence = self.ml_detector.predict(state)
            if ml_anomaly:
                all_anomalies.append({
                    "anomaly_type": "ML_ANOMALY",
                    "severity": AnomalySeverity.MEDIUM,
                    "confidence": confidence,
                    "description": "Machine learning model detected anomalous operating condition",
                    "parameter": "combined",
                    "value": confidence,
                    "threshold": 0.5,
                })
        
        if all_anomalies:
            self.last_anomaly_time = time.time()
            highest_severity = max(all_anomalies, key=lambda x: self._severity_rank(x["severity"]))
            state.anomaly_detected = True
            state.anomaly_type = highest_severity["anomaly_type"]
            state.anomaly_severity = highest_severity["severity"]
        else:
            state.anomaly_detected = False
            state.anomaly_type = None
            state.anomaly_severity = AnomalySeverity.INFO
        
        return all_anomalies
    
    def _severity_rank(self, severity: AnomalySeverity) -> int:
        ranks = {
            AnomalySeverity.INFO: 0,
            AnomalySeverity.LOW: 1,
            AnomalySeverity.MEDIUM: 2,
            AnomalySeverity.HIGH: 3,
            AnomalySeverity.CRITICAL: 4,
        }
        return ranks.get(severity, 0)
    
    def train_ml_model(self, states: list) -> dict:
        return self.ml_detector.train(states)
    
    def get_config(self) -> AnomalyDetectionConfig:
        return self.config
    
    def update_config(self, config: AnomalyDetectionConfig):
        self.config = config


anomaly_detector = AnomalyDetector()