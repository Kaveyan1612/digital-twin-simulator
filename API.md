# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

Currently no authentication required. For production, implement JWT or API key authentication.

## Endpoints

### Health Check

#### GET /api/health

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "simulation_running": true,
  "database": "connected",
  "websocket_clients": 1,
  "uptime_seconds": 3600.5
}
```

**Status Values:**
- `healthy` - All systems operational
- `degraded` - Database disconnected but simulation running

---

### Digital Twin State

#### GET /api/twin/state

Returns current motor state.

**Response:**
```json
{
  "timestamp": 1720000000.123,
  "motor_id": "MOTOR-001",
  "running": true,
  "operating_mode": "NORMAL",
  "target_speed": 3000.0,
  "speed": 2950.0,
  "load": 50.0,
  "torque": 30.0,
  "voltage": 415.0,
  "current": 15.0,
  "power": 5.5,
  "temperature": 65.0,
  "vibration": 1.5,
  "efficiency": 92.0,
  "health_score": 94.0,
  "status": "RUNNING",
  "anomaly_detected": false,
  "anomaly_type": null,
  "anomaly_severity": "INFO"
}
```

#### GET /api/twin/config

Returns motor configuration parameters.

**Response:**
```json
{
  "motor_id": "MOTOR-001",
  "max_speed": 5000.0,
  "max_temperature": 120.0,
  "max_current": 50.0,
  "max_vibration": 10.0,
  "max_load": 100.0,
  "max_voltage": 500.0,
  "rated_power": 15.0,
  "rated_torque": 50.0,
  "rated_speed": 3000.0,
  "rated_current": 25.0,
  "rated_voltage": 415.0,
  "inertia": 0.1,
  "thermal_resistance": 0.5,
  "thermal_capacitance": 100.0,
  "cooling_coefficient": 0.1,
  "friction_coefficient": 0.02,
  "efficiency_base": 0.95
}
```

---

### Motor Control

#### POST /api/twin/start

Starts the motor.

**Response:**
```json
{
  "success": true,
  "message": "Motor started",
  "command_id": 1
}
```

#### POST /api/twin/stop

Stops the motor (controlled deceleration).

**Response:**
```json
{
  "success": true,
  "message": "Motor stop requested",
  "command_id": 2
}
```

#### POST /api/twin/reset

Resets motor to initial state.

**Response:**
```json
{
  "success": true,
  "message": "Motor reset",
  "command_id": 3
}
```

#### POST /api/twin/emergency-stop

Activates emergency stop (immediate).

**Response:**
```json
{
  "success": true,
  "message": "Emergency stop activated",
  "command_id": 4
}
```

#### POST /api/twin/target-speed

Sets target speed.

**Request:**
```json
{
  "value": 3500
}
```

**Constraints:** 0 ≤ value ≤ max_speed (5000)

**Response:**
```json
{
  "success": true,
  "message": "Target speed set to 3500 RPM",
  "command_id": 5
}
```

#### POST /api/twin/load

Sets mechanical load.

**Request:**
```json
{
  "value": 75
}
```

**Constraints:** 0 ≤ value ≤ max_load (100)

**Response:**
```json
{
  "success": true,
  "message": "Load set to 75%",
  "command_id": 6
}
```

#### POST /api/twin/voltage

Sets supply voltage.

**Request:**
```json
{
  "value": 415
}
```

**Constraints:** 0 ≤ value ≤ max_voltage (500)

**Response:**
```json
{
  "success": true,
  "message": "Voltage set to 415V",
  "command_id": 7
}
```

#### POST /api/twin/operating-mode

Sets operating mode.

**Request:**
```json
{
  "value": "HIGH_LOAD"
}
```

**Valid Modes:** `NORMAL`, `HIGH_LOAD`, `COOLING`, `MAINTENANCE`, `FAULT_TEST`

**Response:**
```json
{
  "success": true,
  "message": "Operating mode set to HIGH_LOAD",
  "command_id": 8
}
```

#### POST /api/twin/inject-fault

Injects a fault for testing.

**Request:**
```json
{
  "fault": "overtemperature",
  "value": 1.0
}
```

**Fault Types:**
- `overtemperature`
- `overcurrent`
- `high_vibration`
- `overspeed`
- `undervoltage`
- `overload`
- `sensor_anomaly`
- `combined`

**Intensity:** 0.0 to 1.0 (default 1.0)

**Response:**
```json
{
  "success": true,
  "message": "Fault overtemperature injected",
  "command_id": 9
}
```

#### POST /api/twin/clear-fault

Clears active fault.

**Response:**
```json
{
  "success": true,
  "message": "Fault cleared",
  "command_id": 10
}
```

---

### Historical Data

#### GET /api/twin/history

Retrieves historical motor states.

**Query Parameters:**
- `hours` (int, default: 1, max: 168) - Time range in hours
- `limit` (int, default: 1000, max: 10000) - Maximum records

**Response:**
```json
[
  {
    "timestamp": 1720000000.0,
    "speed": 2950.0,
    "target_speed": 3000.0,
    "load": 50.0,
    "torque": 30.0,
    "voltage": 415.0,
    "current": 15.0,
    "power": 5.5,
    "temperature": 65.0,
    "vibration": 1.5,
    "efficiency": 92.0,
    "health_score": 94.0
  }
]
```

#### GET /api/twin/statistics

Returns statistical summary for time range.

**Query Parameters:**
- `hours` (int, default: 1, max: 168) - Time range in hours

**Response:**
```json
{
  "avg_speed": 2950.0,
  "max_speed": 3000.0,
  "avg_temperature": 65.0,
  "max_temperature": 72.0,
  "avg_load": 50.0,
  "avg_current": 15.0,
  "avg_power": 5.5,
  "avg_efficiency": 92.0,
  "avg_vibration": 1.5,
  "min_health_score": 94.0,
  "data_points": 500,
  "anomaly_count": 3,
  "critical_fault_count": 0,
  "uptime_seconds": 3600.0
}
```

---

### WebSocket

#### WS /ws/twin

Real-time bidirectional communication.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/twin');
```

**Server → Client Messages:**

**Connection Confirmation:**
```json
{
  "type": "connection",
  "timestamp": 1720000000.123,
  "data": {
    "status": "connected",
    "motor_id": "MOTOR-001"
  }
}
```

**Twin State (5 Hz):**
```json
{
  "type": "twin_state",
  "timestamp": 1720000000.123,
  "data": { ...MotorState }
}
```

**Anomaly Detected:**
```json
{
  "type": "anomaly",
  "timestamp": 1720000000.123,
  "data": {
    "anomaly_detected": true,
    "severity": "HIGH",
    "anomaly_type": "OVERTEMPERATURE_WARNING",
    "confidence": 1.0,
    "description": "Motor temperature exceeds warning threshold",
    "parameter": "temperature",
    "value": 95.0,
    "threshold": 90.0
  }
}
```

**Prediction Update:**
```json
{
  "type": "prediction",
  "timestamp": 1720000000.123,
  "data": {
    "prediction_type": "temperature",
    "horizon_seconds": 60,
    "predicted_value": 98.5,
    "confidence": 0.85,
    "timestamp": 1720000000.123,
    "model_version": "1.0"
  }
}
```

**Alert Generated:**
```json
{
  "type": "alert",
  "timestamp": 1720000000.123,
  "data": {
    "id": 1,
    "timestamp": 1720000000.123,
    "alert_type": "OVERTEMPERATURE_WARNING",
    "severity": "HIGH",
    "title": "High Temperature Warning",
    "message": "Motor temperature exceeds warning threshold",
    "parameter": "temperature",
    "current_value": 95.0,
    "threshold_value": 90.0,
    "acknowledged": false
  }
}
```

**Command Acknowledgment:**
```json
{
  "type": "command_ack",
  "timestamp": 1720000000.123,
  "data": {
    "action": "target_speed_set",
    "value": 3500
  }
}
```

**Error:**
```json
{
  "type": "error",
  "timestamp": 1720000000.123,
  "data": {
    "message": "Invalid command: unknown_type"
  }
}
```

**Client → Server Commands:**

```json
{ "type": "set_target_speed", "value": 3500 }
{ "type": "set_load", "value": 75 }
{ "type": "set_voltage", "value": 415 }
{ "type": "start_motor" }
{ "type": "stop_motor" }
{ "type": "reset_motor" }
{ "type": "emergency_stop" }
{ "type": "set_operating_mode", "value": "HIGH_LOAD" }
{ "type": "inject_fault", "fault": "overtemperature", "value": 1.0 }
{ "type": "clear_fault" }
```

---

## Data Models

### MotorState

| Field | Type | Description |
|-------|------|-------------|
| timestamp | float | Unix timestamp |
| motor_id | string | Motor identifier |
| running | boolean | Motor running state |
| operating_mode | enum | NORMAL, HIGH_LOAD, COOLING, MAINTENANCE, FAULT_TEST |
| target_speed | float | Target RPM |
| speed | float | Current RPM |
| load | float | Load percentage |
| torque | float | Torque (Nm) |
| voltage | float | Supply voltage (V) |
| current | float | Current (A) |
| power | float | Power (kW) |
| temperature | float | Temperature (°C) |
| vibration | float | Vibration (mm/s) |
| efficiency | float | Efficiency (%) |
| health_score | float | Health score (0-100) |
| status | enum | STOPPED, STARTING, RUNNING, STOPPING, EMERGENCY_STOP, FAULT, MAINTENANCE |
| anomaly_detected | boolean | Any anomaly active |
| anomaly_type | string|null | Active anomaly type |
| anomaly_severity | enum | INFO, LOW, MEDIUM, HIGH, CRITICAL |

### AnomalyResult

| Field | Type | Description |
|-------|------|-------------|
| anomaly_detected | boolean | Detection result |
| severity | enum | INFO, LOW, MEDIUM, HIGH, CRITICAL |
| anomaly_type | string | Anomaly identifier |
| confidence | float | 0.0-1.0 |
| timestamp | float | Detection time |
| description | string | Human-readable description |
| parameter | string|null | Related parameter |
| value | float|null | Current value |
| threshold | float|null | Threshold crossed |

### AlertInfo

| Field | Type | Description |
|-------|------|-------------|
| id | int | Database ID |
| timestamp | float | Alert time |
| alert_type | string | Alert category |
| severity | enum | INFO, LOW, MEDIUM, HIGH, CRITICAL |
| title | string | Short title |
| message | string | Full message |
| parameter | string|null | Related parameter |
| current_value | float|null | Current reading |
| threshold_value | float|null | Threshold |
| acknowledged | boolean | User acknowledgment |

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid fault type"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "value"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

No rate limiting currently implemented. For production, add rate limiting middleware.

---

## Swagger Documentation

Interactive API docs available at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc