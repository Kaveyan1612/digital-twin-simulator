from typing import List, Optional
from app.schemas.motor import MotorState, AnomalySeverity, AnomalyResult
from app.database.models import Alert
from app.database.repository import AlertRepository
from app.database.database import get_async_session
from app.core.logging import logger
import time


class AlertService:
    def __init__(self):
        self.active_alerts: dict = {}
    
    async def process_anomalies(self, state: MotorState, anomalies: List[dict]):
        for anomaly in anomalies:
            await self._create_alert(state, anomaly)
    
    async def _create_alert(self, state: MotorState, anomaly: dict):
        alert_key = f"{state.motor_id}_{anomaly['anomaly_type']}"
        
        if alert_key in self.active_alerts:
            return
        
        alert = Alert(
            motor_id=state.motor_id,
            alert_type=anomaly["anomaly_type"],
            severity=anomaly["severity"].value if hasattr(anomaly["severity"], "value") else str(anomaly["severity"]),
            title=self._get_alert_title(anomaly["anomaly_type"]),
            message=anomaly["description"],
            parameter=anomaly.get("parameter"),
            current_value=anomaly.get("value"),
            threshold_value=anomaly.get("threshold"),
        )
        
        async for session in get_async_session():
            repo = AlertRepository(session)
            await repo.create(alert)
        
        self.active_alerts[alert_key] = alert
        logger.warning(f"Alert created: {alert.title} - {alert.message}")
    
    def _get_alert_title(self, anomaly_type: str) -> str:
        titles = {
            "OVERTEMPERATURE_WARNING": "High Temperature Warning",
            "OVERTEMPERATURE_CRITICAL": "Critical Temperature",
            "OVERCURRENT_WARNING": "High Current Warning",
            "OVERCURRENT_CRITICAL": "Critical Overcurrent",
            "OVERSPEED_WARNING": "Overspeed Warning",
            "OVERSPEED_CRITICAL": "Critical Overspeed",
            "HIGH_VIBRATION_WARNING": "High Vibration Warning",
            "HIGH_VIBRATION_CRITICAL": "Critical Vibration",
            "OVERLOAD_WARNING": "Overload Warning",
            "UNDERVOLTAGE_WARNING": "Undervoltage Warning",
            "LOW_EFFICIENCY_WARNING": "Low Efficiency",
            "HEALTH_DEGRADED": "Health Degraded",
            "SPEED_DEVIATION_PERSISTENT": "Persistent Speed Deviation",
            "ML_ANOMALY": "ML Anomaly Detected",
            "PREDICTIVE_OVERTEMPERATURE": "Predictive Overheating",
            "PREDICTIVE_HIGH_VIBRATION": "Predictive High Vibration",
            "PREDICTIVE_HEALTH_DEGRADED": "Predictive Health Degradation",
        }
        return titles.get(anomaly_type, anomaly_type.replace("_", " ").title())
    
    async def clear_alert(self, motor_id: str, anomaly_type: str):
        alert_key = f"{motor_id}_{anomaly_type}"
        if alert_key in self.active_alerts:
            del self.active_alerts[alert_key]
    
    async def acknowledge_alert(self, alert_id: int):
        async for session in get_async_session():
            repo = AlertRepository(session)
            alerts = await repo.get_recent("", hours=24, limit=1000)
            for alert in alerts:
                if alert.id == alert_id:
                    alert.acknowledged = True
                    await session.commit()
                    break
    
    async def get_active_alerts(self, motor_id: str) -> List[Alert]:
        async for session in get_async_session():
            repo = AlertRepository(session)
            return await repo.get_unacknowledged(motor_id)


alert_service = AlertService()