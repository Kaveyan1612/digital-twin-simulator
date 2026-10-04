import numpy as np
from typing import List, Dict, Optional
from app.schemas.motor import MotorState
from app.core.config import settings
from app.core.logging import logger


class SimplePredictor:
    def __init__(self):
        self.temperature_history: List[float] = []
        self.vibration_history: List[float] = []
        self.speed_history: List[float] = []
        self.health_history: List[float] = []
        self.max_history = 100
    
    def update(self, state: MotorState):
        self.temperature_history.append(state.temperature)
        self.vibration_history.append(state.vibration)
        self.speed_history.append(state.speed)
        self.health_history.append(state.health_score)
        
        for hist in [self.temperature_history, self.vibration_history, self.speed_history, self.health_history]:
            if len(hist) > self.max_history:
                hist.pop(0)
    
    def predict_temperature(self, horizon_seconds: int, dt: float = 1.0) -> List[float]:
        if len(self.temperature_history) < 5:
            return [self.temperature_history[-1]] * (horizon_seconds // int(dt)) if self.temperature_history else [25.0] * (horizon_seconds // int(dt))
        
        recent = self.temperature_history[-10:]
        if len(recent) >= 2:
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
        else:
            trend = 0
        
        steps = horizon_seconds // int(dt)
        predictions = []
        last = self.temperature_history[-1]
        for i in range(steps):
            last += trend * dt
            predictions.append(max(25, last))
        
        return predictions
    
    def predict_vibration(self, horizon_seconds: int, dt: float = 1.0) -> List[float]:
        if len(self.vibration_history) < 5:
            return [self.vibration_history[-1]] * (horizon_seconds // int(dt)) if self.vibration_history else [0.5] * (horizon_seconds // int(dt))
        
        recent = self.vibration_history[-10:]
        if len(recent) >= 2:
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
        else:
            trend = 0
        
        steps = horizon_seconds // int(dt)
        predictions = []
        last = self.vibration_history[-1]
        for i in range(steps):
            last += trend * dt
            predictions.append(max(0.1, last))
        
        return predictions
    
    def predict_speed(self, horizon_seconds: int, dt: float = 1.0, target_speed: float = 0) -> List[float]:
        if len(self.speed_history) < 5:
            return [self.speed_history[-1]] * (horizon_seconds // int(dt)) if self.speed_history else [0.0] * (horizon_seconds // int(dt))
        
        recent = self.speed_history[-10:]
        if len(recent) >= 2:
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
        else:
            trend = 0
        
        steps = horizon_seconds // int(dt)
        predictions = []
        last = self.speed_history[-1]
        for i in range(steps):
            last += trend * dt
            last += (target_speed - last) * 0.1
            predictions.append(max(0, last))
        
        return predictions
    
    def predict_health(self, horizon_seconds: int, dt: float = 1.0) -> List[float]:
        if len(self.health_history) < 5:
            return [self.health_history[-1]] * (horizon_seconds // int(dt)) if self.health_history else [100.0] * (horizon_seconds // int(dt))
        
        recent = self.health_history[-10:]
        if len(recent) >= 2:
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
        else:
            trend = 0
        
        steps = horizon_seconds // int(dt)
        predictions = []
        last = self.health_history[-1]
        for i in range(steps):
            last += trend * dt
            predictions.append(np.clip(last, 0, 100))
        
        return predictions


class MLPredictor:
    def __init__(self):
        self.models: Dict[str, any] = {}
        self.scalers: Dict[str, any] = {}
        self.trained = False
    
    def train(self, states: List[MotorState]) -> dict:
        if len(states) < 100:
            logger.warning("Insufficient data for ML predictor training")
            return {"success": False, "message": "Insufficient training data"}
        
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            import joblib
            import os
            
            features = []
            temp_targets = []
            vib_targets = []
            speed_targets = []
            health_targets = []
            
            for i in range(len(states) - 10):
                feat = np.array([
                    states[i].speed / 5000.0,
                    states[i].target_speed / 5000.0,
                    states[i].load / 100.0,
                    states[i].torque / 100.0,
                    states[i].voltage / 500.0,
                    states[i].current / 50.0,
                    states[i].power / 20.0,
                    states[i].temperature / 150.0,
                    states[i].vibration / 10.0,
                    states[i].efficiency,
                    states[i].health_score / 100.0,
                    1.0 if states[i].running else 0.0,
                ])
                features.append(feat)
                temp_targets.append(states[i + 10].temperature / 150.0)
                vib_targets.append(states[i + 10].vibration / 10.0)
                speed_targets.append(states[i + 10].speed / 5000.0)
                health_targets.append(states[i + 10].health_score / 100.0)
            
            X = np.array(features)
            y_temp = np.array(temp_targets)
            y_vib = np.array(vib_targets)
            y_speed = np.array(speed_targets)
            y_health = np.array(health_targets)
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            X_train, X_test, y_train_temp, y_test_temp = train_test_split(X_scaled, y_temp, test_size=0.2, random_state=42)
            _, _, y_train_vib, y_test_vib = train_test_split(X_scaled, y_vib, test_size=0.2, random_state=42)
            _, _, y_train_speed, y_test_speed = train_test_split(X_scaled, y_speed, test_size=0.2, random_state=42)
            _, _, y_train_health, y_test_health = train_test_split(X_scaled, y_health, test_size=0.2, random_state=42)
            
            models = {}
            metrics = {}
            
            for name, y_train, y_test in [
                ("temperature", y_train_temp, y_test_temp),
                ("vibration", y_train_vib, y_test_vib),
                ("speed", y_train_speed, y_test_speed),
                ("health", y_train_health, y_test_health),
            ]:
                model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
                model.fit(X_train, y_train)
                pred = model.predict(X_test)
                
                models[name] = model
                metrics[name] = {
                    "mae": mean_absolute_error(y_test, pred),
                    "rmse": np.sqrt(mean_squared_error(y_test, pred)),
                    "r2": r2_score(y_test, pred),
                }
            
            self.models = models
            self.scalers = {"main": scaler}
            self.trained = True
            
            model_dir = os.path.join(os.path.dirname(settings.database_url.replace("sqlite:///", "").replace("sqlite+aiosqlite:///", "")), "..", "models")
            os.makedirs(model_dir, exist_ok=True)
            
            for name, model in models.items():
                joblib.dump(model, os.path.join(model_dir, f"{name}_predictor.pkl"))
            joblib.dump(scaler, os.path.join(model_dir, "predictor_scaler.pkl"))
            
            logger.info("ML Predictors trained successfully")
            return {"success": True, "metrics": metrics}
            
        except Exception as e:
            logger.error(f"ML Predictor training failed: {e}")
            return {"success": False, "message": str(e)}
    
    def predict(self, state: MotorState, horizon_seconds: int) -> Dict[str, List[float]]:
        if not self.trained:
            return {}
        
        try:
            feat = np.array([[
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
            ]])
            
            feat_scaled = self.scalers["main"].transform(feat)
            
            results = {}
            for name, model in self.models.items():
                pred = model.predict(feat_scaled)[0]
                if name == "temperature":
                    results[name] = [pred * 150.0] * (horizon_seconds // 10)
                elif name == "vibration":
                    results[name] = [pred * 10.0] * (horizon_seconds // 10)
                elif name == "speed":
                    results[name] = [pred * 5000.0] * (horizon_seconds // 10)
                elif name == "health":
                    results[name] = [pred * 100.0] * (horizon_seconds // 10)
            
            return results
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {}


class PredictionEngine:
    def __init__(self):
        self.simple_predictor = SimplePredictor()
        self.ml_predictor = MLPredictor()
        self.enabled = settings.prediction_enabled
        self.horizon_seconds = 60
        self.update_interval = 10
        self.last_update = 0
    
    def update(self, state: MotorState):
        if not self.enabled:
            return
        self.simple_predictor.update(state)
    
    def get_forecasts(self, state: MotorState) -> Dict[str, List[Dict]]:
        if not self.enabled:
            return {}
        
        forecasts = {}
        dt = 1.0
        
        temp_preds = self.simple_predictor.predict_temperature(self.horizon_seconds, dt)
        forecasts["temperature"] = [
            {"time": i * dt, "value": round(v, 1)}
            for i, v in enumerate(temp_preds)
        ]
        
        vib_preds = self.simple_predictor.predict_vibration(self.horizon_seconds, dt)
        forecasts["vibration"] = [
            {"time": i * dt, "value": round(v, 2)}
            for i, v in enumerate(vib_preds)
        ]
        
        speed_preds = self.simple_predictor.predict_speed(self.horizon_seconds, dt, state.target_speed)
        forecasts["speed"] = [
            {"time": i * dt, "value": round(v, 1)}
            for i, v in enumerate(speed_preds)
        ]
        
        health_preds = self.simple_predictor.predict_health(self.horizon_seconds, dt)
        forecasts["health_score"] = [
            {"time": i * dt, "value": round(v, 1)}
            for i, v in enumerate(health_preds)
        ]
        
        if self.ml_predictor.trained:
            ml_preds = self.ml_predictor.predict(state, self.horizon_seconds)
            for name, preds in ml_preds.items():
                if name in forecasts:
                    for i, pred in enumerate(preds):
                        if i < len(forecasts[name]):
                            forecasts[name][i]["ml_value"] = round(pred, 1)
        
        return forecasts
    
    def get_warnings(self, state: MotorState) -> List[Dict]:
        warnings = []
        forecasts = self.get_forecasts(state)
        
        if "temperature" in forecasts:
            for pred in forecasts["temperature"]:
                if pred["value"] > 90:
                    warnings.append({
                        "type": "PREDICTIVE_OVERTEMPERATURE",
                        "message": f"Temperature predicted to reach {pred['value']:.1f}°C in {pred['time']:.0f}s",
                        "severity": "HIGH" if pred["value"] > 110 else "MEDIUM",
                        "parameter": "temperature",
                        "predicted_value": pred["value"],
                        "threshold": 90,
                        "time_to_threshold": pred["time"],
                    })
                    break
        
        if "vibration" in forecasts:
            for pred in forecasts["vibration"]:
                if pred["value"] > 8:
                    warnings.append({
                        "type": "PREDICTIVE_HIGH_VIBRATION",
                        "message": f"Vibration predicted to reach {pred['value']:.2f} mm/s in {pred['time']:.0f}s",
                        "severity": "HIGH",
                        "parameter": "vibration",
                        "predicted_value": pred["value"],
                        "threshold": 8,
                        "time_to_threshold": pred["time"],
                    })
                    break
        
        if "health_score" in forecasts:
            for pred in forecasts["health_score"]:
                if pred["value"] < 30:
                    warnings.append({
                        "type": "PREDICTIVE_HEALTH_DEGRADED",
                        "message": f"Health score predicted to drop to {pred['value']:.1f}% in {pred['time']:.0f}s",
                        "severity": "MEDIUM",
                        "parameter": "health_score",
                        "predicted_value": pred["value"],
                        "threshold": 30,
                        "time_to_threshold": pred["time"],
                    })
                    break
        
        return warnings


prediction_engine = PredictionEngine()