from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.database.models import MotorState, Anomaly, Alert, Command, Prediction, SystemEvent
from app.core.logging import logger


class MotorStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, state: MotorState) -> MotorState:
        self.session.add(state)
        await self.session.flush()
        await self.session.refresh(state)
        return state
    
    async def get_latest(self, motor_id: str) -> Optional[MotorState]:
        stmt = select(MotorState).where(MotorState.motor_id == motor_id).order_by(desc(MotorState.timestamp)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_history(
        self, 
        motor_id: str, 
        start_time: datetime, 
        end_time: datetime,
        limit: int = 1000
    ) -> List[MotorState]:
        stmt = (
            select(MotorState)
            .where(MotorState.motor_id == motor_id)
            .where(MotorState.timestamp >= start_time)
            .where(MotorState.timestamp <= end_time)
            .order_by(MotorState.timestamp)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_statistics(
        self, 
        motor_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> dict:
        stmt = select(
            func.avg(MotorState.speed),
            func.max(MotorState.speed),
            func.avg(MotorState.temperature),
            func.max(MotorState.temperature),
            func.avg(MotorState.load),
            func.avg(MotorState.current),
            func.avg(MotorState.power),
            func.avg(MotorState.efficiency),
            func.avg(MotorState.vibration),
            func.min(MotorState.health_score),
            func.count(MotorState.id)
        ).where(
            MotorState.motor_id == motor_id,
            MotorState.timestamp >= start_time,
            MotorState.timestamp <= end_time
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return {
            "avg_speed": row[0] or 0,
            "max_speed": row[1] or 0,
            "avg_temperature": row[2] or 0,
            "max_temperature": row[3] or 0,
            "avg_load": row[4] or 0,
            "avg_current": row[5] or 0,
            "avg_power": row[6] or 0,
            "avg_efficiency": row[7] or 0,
            "avg_vibration": row[8] or 0,
            "min_health_score": row[9] or 100,
            "data_points": row[10] or 0
        }


class AnomalyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, anomaly: Anomaly) -> Anomaly:
        self.session.add(anomaly)
        await self.session.flush()
        await self.session.refresh(anomaly)
        return anomaly
    
    async def get_recent(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Anomaly]:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Anomaly)
            .where(Anomaly.motor_id == motor_id)
            .where(Anomaly.timestamp >= since)
            .order_by(desc(Anomaly.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_by_type(self, motor_id: str, hours: int = 24) -> dict:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Anomaly.anomaly_type, func.count(Anomaly.id))
            .where(Anomaly.motor_id == motor_id)
            .where(Anomaly.timestamp >= since)
            .group_by(Anomaly.anomaly_type)
        )
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}


class AlertRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, alert: Alert) -> Alert:
        self.session.add(alert)
        await self.session.flush()
        await self.session.refresh(alert)
        return alert
    
    async def get_recent(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Alert]:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Alert)
            .where(Alert.motor_id == motor_id)
            .where(Alert.timestamp >= since)
            .order_by(desc(Alert.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_unacknowledged(self, motor_id: str) -> List[Alert]:
        stmt = (
            select(Alert)
            .where(Alert.motor_id == motor_id)
            .where(Alert.acknowledged == False)
            .order_by(desc(Alert.timestamp))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CommandRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, command: Command) -> Command:
        self.session.add(command)
        await self.session.flush()
        await self.session.refresh(command)
        return command
    
    async def get_recent(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Command]:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Command)
            .where(Command.motor_id == motor_id)
            .where(Command.timestamp >= since)
            .order_by(desc(Command.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PredictionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, prediction: Prediction) -> Prediction:
        self.session.add(prediction)
        await self.session.flush()
        await self.session.refresh(prediction)
        return prediction
    
    async def get_latest(self, motor_id: str, prediction_type: str) -> Optional[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.motor_id == motor_id)
            .where(Prediction.prediction_type == prediction_type)
            .order_by(desc(Prediction.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_recent(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[Prediction]:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Prediction)
            .where(Prediction.motor_id == motor_id)
            .where(Prediction.timestamp >= since)
            .order_by(desc(Prediction.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SystemEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, event: SystemEvent) -> SystemEvent:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event
    
    async def get_recent(self, motor_id: str, hours: int = 24, limit: int = 100) -> List[SystemEvent]:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(SystemEvent)
            .where(SystemEvent.motor_id == motor_id)
            .where(SystemEvent.timestamp >= since)
            .order_by(desc(SystemEvent.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def cleanup_old_events(self, motor_id: str, days: int = 30) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        stmt = select(SystemEvent).where(
            SystemEvent.motor_id == motor_id,
            SystemEvent.timestamp < cutoff
        )
        result = await self.session.execute(stmt)
        events = list(result.scalars().all())
        for event in events:
            await self.session.delete(event)
        return len(events)