import os
import joblib
import numpy as np
from typing import Dict, Optional, Any
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from app.core.config import settings
from app.core.logging import logger


class PredictionModelManager:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_dir = os.path.join(
            os.path.dirname(settings.database_url.replace("sqlite:///", "").replace("sqlite+aiosqlite:///", "")),
            "..", "models"
        )
        os.makedirs(self.model_dir, exist_ok=True)
    
    def train_linear(self, X: np.ndarray, y: np.ndarray) -> LinearRegression:
        model = LinearRegression()
        model.fit(X, y)
        return model
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray, n_estimators: int = 100) -> RandomForestRegressor:
        model = RandomForestRegressor(n_estimators=n_estimators, max_depth=15, random_state=42, n_jobs=-1)
        model.fit(X, y)
        return model
    
    def train_gradient_boosting(self, X: np.ndarray, y: np.ndarray, n_estimators: int = 100) -> GradientBoostingRegressor:
        model = GradientBoostingRegressor(n_estimators=n_estimators, max_depth=5, random_state=42)
        model.fit(X, y)
        return model
    
    def save_model(self, name: str, model: Any, scaler: StandardScaler = None):
        joblib.dump(model, os.path.join(self.model_dir, f"{name}_model.pkl"))
        if scaler:
            joblib.dump(scaler, os.path.join(self.model_dir, f"{name}_scaler.pkl"))
        logger.info(f"Saved model: {name}")
    
    def load_model(self, name: str) -> tuple:
        model_path = os.path.join(self.model_dir, f"{name}_model.pkl")
        scaler_path = os.path.join(self.model_dir, f"{name}_scaler.pkl")
        
        model = None
        scaler = None
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
        
        return model, scaler
    
    def load_all(self) -> Dict[str, tuple]:
        model_types = ["temperature", "vibration", "speed", "health"]
        loaded = {}
        for mtype in model_types:
            model, scaler = self.load_model(mtype)
            if model:
                self.models[mtype] = model
                self.scalers[mtype] = scaler
                loaded[mtype] = (model, scaler)
        return loaded


model_manager = PredictionModelManager()