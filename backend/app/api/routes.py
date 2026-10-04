from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Optional
from app.database.database import get_async_session
from app.database.models import MotorState as DBMotorState
from app.schemas.motor import (
    MotorState, MotorConfig, CommandRequest, CommandResponse,
    HistoricalDataPoint, StatisticsResponse
)
from app.twin.state import digital_twin
from app.twin.faults import FaultType
from app.services.history_service import history_service
from app.core.logging import logger
import time


router = APIRouter(prefix="/api/twin", tags=["digital-twin"])


@router.get("/state", response_model=MotorState)
async def get_current_state():
    return digital_twin.get_state()


@router.get("/config", response_model=MotorConfig)
async def get_config():
    return digital_twin.get_config()


@router.post("/start", response_model=CommandResponse)
async def start_motor():
    try:
        digital_twin.start_motor()
        await _log_command("start_motor", {})
        return CommandResponse(success=True, message="Motor started")
    except Exception as e:
        logger.error(f"Failed to start motor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=CommandResponse)
async def stop_motor():
    try:
        digital_twin.stop_motor()
        await _log_command("stop_motor", {})
        return CommandResponse(success=True, message="Motor stop requested")
    except Exception as e:
        logger.error(f"Failed to stop motor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", response_model=CommandResponse)
async def reset_motor():
    try:
        digital_twin.reset_motor()
        await _log_command("reset_motor", {})
        return CommandResponse(success=True, message="Motor reset")
    except Exception as e:
        logger.error(f"Failed to reset motor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-stop", response_model=CommandResponse)
async def emergency_stop():
    try:
        digital_twin.emergency_stop()
        await _log_command("emergency_stop", {})
        return CommandResponse(success=True, message="Emergency stop activated")
    except Exception as e:
        logger.error(f"Failed to emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/target-speed", response_model=CommandResponse)
async def set_target_speed(request: CommandRequest):
    if request.value is None:
        raise HTTPException(status_code=400, detail="Value required")
    
    try:
        speed = max(0, min(request.value, digital_twin.params.max_speed))
        digital_twin.set_target_speed(speed)
        await _log_command("set_target_speed", {"value": speed})
        return CommandResponse(success=True, message=f"Target speed set to {speed} RPM")
    except Exception as e:
        logger.error(f"Failed to set target speed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load", response_model=CommandResponse)
async def set_load(request: CommandRequest):
    if request.value is None:
        raise HTTPException(status_code=400, detail="Value required")
    
    try:
        load = max(0, min(request.value, digital_twin.params.max_load))
        digital_twin.set_load(load)
        await _log_command("set_load", {"value": load})
        return CommandResponse(success=True, message=f"Load set to {load}%")
    except Exception as e:
        logger.error(f"Failed to set load: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voltage", response_model=CommandResponse)
async def set_voltage(request: CommandRequest):
    if request.value is None:
        raise HTTPException(status_code=400, detail="Value required")
    
    try:
        voltage = max(0, min(request.value, digital_twin.params.max_voltage))
        digital_twin.set_voltage(voltage)
        await _log_command("set_voltage", {"value": voltage})
        return CommandResponse(success=True, message=f"Voltage set to {voltage}V")
    except Exception as e:
        logger.error(f"Failed to set voltage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/operating-mode", response_model=CommandResponse)
async def set_operating_mode(request: CommandRequest):
    if request.value is None:
        raise HTTPException(status_code=400, detail="Mode required")
    
    try:
        mode = str(request.value).upper()
        valid_modes = ["NORMAL", "HIGH_LOAD", "COOLING", "MAINTENANCE", "FAULT_TEST"]
        if mode not in valid_modes:
            raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {valid_modes}")
        
        digital_twin.set_operating_mode(mode)
        await _log_command("set_operating_mode", {"mode": mode})
        return CommandResponse(success=True, message=f"Operating mode set to {mode}")
    except Exception as e:
        logger.error(f"Failed to set operating mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inject-fault", response_model=CommandResponse)
async def inject_fault(request: CommandRequest):
    if request.fault is None:
        raise HTTPException(status_code=400, detail="Fault type required")
    
    try:
        fault_type = FaultType(request.fault.value)
        intensity = request.value if request.value is not None else 1.0
        digital_twin.inject_fault(fault_type.value, intensity)
        await _log_command("inject_fault", {"fault": fault_type.value, "intensity": intensity})
        return CommandResponse(success=True, message=f"Fault {fault_type.value} injected")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid fault type")
    except Exception as e:
        logger.error(f"Failed to inject fault: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-fault", response_model=CommandResponse)
async def clear_fault():
    try:
        digital_twin.clear_fault()
        await _log_command("clear_fault", {})
        return CommandResponse(success=True, message="Fault cleared")
    except Exception as e:
        logger.error(f"Failed to clear fault: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[HistoricalDataPoint])
async def get_history(
    hours: int = Query(1, ge=1, le=168),
    limit: int = Query(1000, ge=1, le=10000)
):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    return await history_service.get_history(
        digital_twin.motor_id, start_time, end_time, limit
    )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    hours: int = Query(1, ge=1, le=168)
):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    return await history_service.get_statistics(
        digital_twin.motor_id, start_time, end_time
    )


async def _log_command(command_type: str, parameters: dict):
    await history_service.save_command({
        "motor_id": digital_twin.motor_id,
        "command_type": command_type,
        "parameters": str(parameters),
    })