from pydantic import BaseModel
from typing import Optional, Any, Union
from app.schemas.motor import MotorState, CommandRequest, AnomalyResult, PredictionResult, AlertInfo


class WebSocketMessage(BaseModel):
    type: str
    timestamp: float
    data: Optional[Any] = None


class TwinStateMessage(WebSocketMessage):
    type: str = "twin_state"
    data: MotorState


class AnomalyMessage(WebSocketMessage):
    type: str = "anomaly"
    data: AnomalyResult


class PredictionMessage(WebSocketMessage):
    type: str = "prediction"
    data: PredictionResult


class AlertMessage(WebSocketMessage):
    type: str = "alert"
    data: AlertInfo


class CommandAckMessage(WebSocketMessage):
    type: str = "command_ack"
    data: dict


class ErrorMessage(WebSocketMessage):
    type: str = "error"
    data: dict


class ConnectionMessage(WebSocketMessage):
    type: str = "connection"
    data: dict


WebSocketOutgoingMessage = Union[
    TwinStateMessage,
    AnomalyMessage,
    PredictionMessage,
    AlertMessage,
    CommandAckMessage,
    ErrorMessage,
    ConnectionMessage
]


class WebSocketIncomingMessage(BaseModel):
    type: str
    value: Optional[float] = None
    fault: Optional[str] = None