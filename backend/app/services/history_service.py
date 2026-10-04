from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.database.models import MotorState as DBMotorState, Anomaly, Alert, Command, Prediction, SystemEvent
from app.database.repository import (
    MotorStateRepository,
    AnomalyRepository,
    AlertRepository,
    CommandRepository,
    PredictionRepository,
    SystemEventRepository
)
from app.database.database import get_async_session
from app.schemas.motor import HistoricalDataPoint, StatisticsResponse
from app.core.logging import logger


class HistoryService:
    async def save_state(self, state_dict: dict) -> DBMotorState:
        db_state = DBMotorState(**state_dict)
        async for session in get_async_session():
            repo = MotorStateRepository(session)
            return await repo.create(db_state)
    
    async def save_anomaly(self, anomaly_dict: dict) -> Anomaly:
        anomaly = Anomaly(**anomaly_dict)
        async for session in get_async_session():
            repo = AnomalyRepository(session)
            return await repo.create(anomaly)
    
    async def save_alert(self, alert_dict: dict) -> Alert:
        alert = Alert(**alert_dict)
        async for session in get_async_session():
            repo = AlertRepository(session)
            return await repo.create(alert)
    
    async def save_command(self, command_dict: dict) -> Command:
        command = Command(**command_dict)
        async for session in get_async_session():
            repo = CommandRepository(session)
            return await repo.create(command)
    
    async def save_prediction(self, prediction_dict: dict) -> Prediction:
        prediction = Prediction(**prediction_dict)
        async for session in get_async_session():
            repo = PredictionRepository(session)
            return await repo.create(prediction)
    
    async def save_event(self, event_dict: dict) -> SystemEvent:
        event = SystemEvent(**event_dict)
        async for session in get_async_session():
            repo = SystemEventRepository(session)
            return await repo.create(event)
    
    async def get_history(
        self,
        motor_id: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000
    ) -> List[HistoricalDataPoint]:
        async for session in get_async_session():
            repo = MotorStateRepository(session)
            states = await repo.get_history(motor_id, start_time, end_time, limit)
            
            return [
                HistoricalDataPoint(
                    timestamp=s.timestamp.timestamp(),
                    speed=s.speed,
                    target_speed=s.target_speed,
                    load=s.load,
                    torque=s.torque,
                    voltage=s.voltage,
                    current=s.current,
                    power=s.power,
                    temperature=s.temperature,
                    vibration=s.vibration,
                    efficiency=s.efficiency,
                    health_score=s.health_score,
                )
                for s in states
            ]
    
    async def get_statistics(
        self,
        motor_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> StatisticsResponse:
        async for session in get_async_session():
            state_repo = MotorStateRepository(session)
            anomaly_repo = AnomalyRepository(session)
            
            stats = await state_repo.get_statistics(motor_id, start_time, end_time)
            anomaly_counts = await anomaly_repo.count_by_type(motor_id, hours=24)
            
            critical_count = sum(
                count for atype, count in anomaly_counts.items()
                if "CRITICAL" in atype
            )
            
            uptime = (end_time - start_time).total_seconds()
            
            return StatisticsResponse(
                avg_speed=round(stats["avg_speed"], 1),
                max_speed=round(stats["max_speed"], 1),
                avg_temperature=round(stats["avg_temperature"], 1),
                max_temperature=round(stats["max_temperature"], 1),
                avg_load=round(stats["avg_load"], 1),
                avg_current=round(stats["avg_current"], 1),
                avg_power=round(stats["avg_power"], 2),
                avg_efficiency=round(stats["avg_efficiency"] * 100, 1),
                avg_vibration=round(stats["avg_vibration"], 2),
                min_health_score=round(stats["min_health_score"], 1),
                data_points=stats["data_points"],
                anomaly_count=sum(anomaly_counts.values()),
                critical_fault_count=critical_count,
                uptime_seconds=uptime,
            )
    
    async def get_recent_anomalies(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Anomaly]:
        async for session in get_async_session():
            repo = AnomalyRepository(session)
            return await repo.get_recent(motor_id, hours, limit)
    
    async def get_recent_alerts(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Alert]:
        async for session in get_async_session():
            repo = AlertRepository(session)
            return await repo.get_recent(motor_id, hours, limit)
    
    async def get_recent_commands(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Command]:
        async for session in get_async_session():
            repo = CommandRepository(session)
            return await repo.get_recent(motor_id, hours, limit)
    
    async def get_recent_predictions(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Prediction]:
        async for session in get_async_session():
            repo = PredictionRepository(session)
            return await repo.get_recent(motor_id, hours, limit)
    
    async def get_recent_events(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[SystemEvent]:
        async for session in get_async_session():
            repo = SystemEventRepository(session)
            return await repo.get_recent(motor_id, hours, limit)
    
    async def cleanup_old_data(self, motor_id: str, days: int = 30):
        async for session in get_async_session():
            repo = SystemEventRepository(session)
            await repo.cleanup_old_events(motor_id, days)


history_service = HistoryService()