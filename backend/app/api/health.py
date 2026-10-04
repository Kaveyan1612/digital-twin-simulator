from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_async_session
from app.schemas.motor import HealthResponse
from app.twin.state import digital_twin
from app.core.logging import logger
import time


router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        simulation_running=digital_twin.simulation_engine.running,
        database=db_status,
        websocket_clients=0,
        uptime_seconds=digital_twin.get_uptime(),
    )