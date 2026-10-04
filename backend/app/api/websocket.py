from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Set
import json
import time
from app.database.database import get_async_session
from app.twin.state import digital_twin
from app.anomaly.detector import anomaly_detector
from app.prediction.predictor import prediction_engine
from app.services.alert_service import alert_service
from app.services.history_service import history_service
from app.schemas.motor import MotorState
from app.core.logging import logger


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total clients: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total clients: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        
        for conn in dead_connections:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/ws/twin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connection",
            "timestamp": time.time(),
            "data": {"status": "connected", "motor_id": digital_twin.motor_id}
        })
        
        state = digital_twin.get_state_dict()
        await websocket.send_json({
            "type": "twin_state",
            "timestamp": time.time(),
            "data": state
        })
        
        while True:
            try:
                data = await websocket.receive_json()
                await handle_command(websocket, data)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "timestamp": time.time(),
                    "data": {"message": str(e)}
                })
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


async def handle_command(websocket: WebSocket, data: dict):
    command_type = data.get("type")
    
    try:
        if command_type == "set_target_speed":
            value = data.get("value")
            if value is not None:
                digital_twin.set_target_speed(float(value))
                await _ack(websocket, "target_speed_set", value)
        
        elif command_type == "set_load":
            value = data.get("value")
            if value is not None:
                digital_twin.set_load(float(value))
                await _ack(websocket, "load_set", value)
        
        elif command_type == "set_voltage":
            value = data.get("value")
            if value is not None:
                digital_twin.set_voltage(float(value))
                await _ack(websocket, "voltage_set", value)
        
        elif command_type == "start_motor":
            digital_twin.start_motor()
            await _ack(websocket, "motor_started")
        
        elif command_type == "stop_motor":
            digital_twin.stop_motor()
            await _ack(websocket, "motor_stopped")
        
        elif command_type == "reset_motor":
            digital_twin.reset_motor()
            await _ack(websocket, "motor_reset")
        
        elif command_type == "emergency_stop":
            digital_twin.emergency_stop()
            await _ack(websocket, "emergency_stop_activated")
        
        elif command_type == "set_operating_mode":
            value = data.get("value")
            if value is not None:
                digital_twin.set_operating_mode(str(value))
                await _ack(websocket, "operating_mode_set", value)
        
        elif command_type == "inject_fault":
            fault = data.get("fault")
            intensity = data.get("value", 1.0)
            if fault:
                digital_twin.inject_fault(fault, float(intensity))
                await _ack(websocket, "fault_injected", {"fault": fault, "intensity": intensity})
        
        elif command_type == "clear_fault":
            digital_twin.clear_fault()
            await _ack(websocket, "fault_cleared")
        
        else:
            await websocket.send_json({
                "type": "error",
                "timestamp": time.time(),
                "data": {"message": f"Unknown command: {command_type}"}
            })
    
    except Exception as e:
        logger.error(f"Command handling error: {e}")
        await websocket.send_json({
            "type": "error",
            "timestamp": time.time(),
            "data": {"message": str(e)}
        })


async def _ack(websocket: WebSocket, action: str, value=None):
    await websocket.send_json({
        "type": "command_ack",
        "timestamp": time.time(),
        "data": {"action": action, "value": value}
    })


async def broadcast_state(state_dict: dict):
    state = MotorState(**state_dict)
    
    anomalies = anomaly_detector.detect(state)
    
    for anomaly in anomalies:
        await manager.broadcast({
            "type": "anomaly",
            "timestamp": time.time(),
            "data": anomaly
        })
        await alert_service.process_anomalies(state, [anomaly])
        await history_service.save_anomaly({
            "motor_id": state.motor_id,
            "anomaly_type": anomaly["anomaly_type"],
            "severity": anomaly["severity"].value if hasattr(anomaly["severity"], "value") else str(anomaly["severity"]),
            "confidence": anomaly["confidence"],
            "description": anomaly["description"],
            "parameter": anomaly.get("parameter"),
            "value": anomaly.get("value"),
            "threshold": anomaly.get("threshold"),
        })
    
    predictions = prediction_engine.get_forecasts(state)
    if predictions:
        for pred_type, pred_data in predictions.items():
            await manager.broadcast({
                "type": "prediction",
                "timestamp": time.time(),
                "data": {
                    "prediction_type": pred_type,
                    "predictions": pred_data,
                }
            })
    
    warnings = prediction_engine.get_warnings(state)
    for warning in warnings:
        await manager.broadcast({
            "type": "alert",
            "timestamp": time.time(),
            "data": warning
        })
        await alert_service.process_anomalies(state, [warning])
    
    await history_service.save_state(state_dict)
    
    await manager.broadcast({
        "type": "twin_state",
        "timestamp": time.time(),
        "data": state_dict
    })