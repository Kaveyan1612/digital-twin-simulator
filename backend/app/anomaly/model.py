import numpy as np
import joblib
import os
from typing import Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.anomaly.features import extract_features, normalize_features, FEATURE_NAMES
from app.schemas.motor import MotorState
from app.core.config import settings
from app.core.logging import logger


class MLAnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model: Optional[IsolationForest] = None
        self.scaler = StandardScaler()
        self.contamination = contamination
        self.trained = False
        self.model_path = os.path.join(settings.database_url.replace("sqlite:///", "").replace("sqlite+aiosqlite:///", ""), "..", "models", "anomaly_model.pkl")
        self.scaler_path = os.path.join(settings.database_url.replace("sqlite:///", "").replace("sqlite+aiosqlite:///", ""), "..", "models", "anomaly_scaler.pkl")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def train(self, states: list) -> dict:
        if len(states) < 50:
            logger.warning("Insufficient training data for ML anomaly detector")
            return {"success": False, "message": "Insufficient training data"}
        
        features = np.array([extract_features(s) for s in states])
        features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0)
        
        self.scaler.fit(features)
        normalized = self.scaler.transform(features)
        
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto'
        )
        self.model.fit(normalized)
        
        self.trained = True
        self.save()
        
        scores = self.model.score_samples(normalized)
        predictions = self.model.predict(normalized)
        anomaly_count = np.sum(predictions == -1)
        
        logger.info(f"ML Anomaly detector trained on {len(states)} samples. Anomalies detected: {anomaly_count}")
        
        return {
            "success": True,
            "training_samples": len(states),
            "anomalies_detected": int(anomaly_count),
            "anomaly_ratio": float(anomaly_count / len(states)),
        }
    
    def predict(self, state: MotorState) -> Tuple[bool, float]:
        if not self.trained or self.model is None:
            return False, 0.0
        
        features = extract_features(state).reshape(1, -1)
        features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0)
        normalized = self.scaler.transform(features)
        
        score = self.model.score_samples(normalized)[0]
        prediction = self.model.predict(normalized)[0]
        
        is_anomaly = prediction == -1
        confidence = min(1.0, max(0.0, (0.5 - score) * 2))
        
        return is_anomaly, confidence
    
    def predict_batch(self, states: list) -> list:
        if not self.trained or self.model is None:
            return [(False, 0.0)] * len(states)
        
        features = np.array([extract_features(s) for s in states])
        features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0)
        normalized = self.scaler.transform(features)
        
        scores = self.model.score_samples(normalized)
        predictions = self.model.predict(normalized)
        
        results = []
        for score, pred in zip(scores, predictions):
            is_anomaly = pred == -1
            confidence = min(1.0, max(0.0, (0.5 - score) * 2))
            results.append((is_anomaly, confidence))
        
        return results
    
    def save(self):
        if self.model:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info(f"ML model saved to {self.model_path}")
    
    def load(self) -> bool:
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.trained = True
                logger.info("ML anomaly model loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
        return False


ml_anomaly_detector = MLAnomalyDetector()