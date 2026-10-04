# Architecture Documentation

## System Overview

The Digital Twin Simulator follows a clean, modular architecture with clear separation of concerns between the frontend, backend, simulation engine, and data layers.

## Backend Architecture

### Core Components

#### 1. Digital Twin Engine (`app/twin/`)
- **MotorModel** (`motor_model.py`): Physics-based simulation of electric motor
- **SimulationEngine** (`engine.py`): Async background task running at 10 Hz
- **DigitalTwin** (`state.py`): High-level facade for twin operations
- **Parameters** (`parameters.py`): Motor configuration constants
- **Faults** (`faults.py`): Fault injection system

#### 2. Anomaly Detection (`app/anomaly/`)
- **RuleEngine** (`rules.py`): Deterministic threshold-based detection
- **MLAnomalyDetector** (`model.py`): Isolation Forest for ML-based detection
- **AnomalyDetector** (`detector.py`): Orchestrates both detection methods
- **Features** (`features.py`): Feature extraction for ML

#### 3. Prediction Engine (`app/prediction/`)
- **PredictionEngine** (`predictor.py`): Forecasts future parameter values
- **SimplePredictor**: Linear trend extrapolation
- **MLPredictor**: Random Forest regression models
- **Features/Models**: Feature extraction and model management

#### 4. Services (`app/services/`)
- **AlertService**: Manages alert lifecycle
- **HealthService**: Calculates health scores
- **HistoryService**: Data persistence and retrieval

#### 5. Database (`app/database/`)
- **Models** (`models.py`): SQLModel definitions
- **Database** (`database.py`): Connection management
- **Repository** (`repository.py`): Data access layer

#### 6. API Layer (`app/api/`)
- **Routes** (`routes.py`): REST endpoints
- **WebSocket** (`websocket.py`): Real-time communication
- **Health** (`health.py`): Health check endpoint

### Data Flow

```
Simulation Loop (10 Hz)
        │
        ▼
MotorModel.update(dt) ──► DigitalTwin.get_state()
        │
        ▼
AnomalyDetector.detect() ──► AlertService.process()
        │
        ▼
PredictionEngine.get_forecasts() ──► Warning generation
        │
        ▼
HistoryService.save_state()
        │
        ▼
WebSocket broadcast (5 Hz) ──► Frontend
```

### Async Architecture

The simulation runs in a dedicated asyncio task:
- Non-blocking FastAPI event loop
- WebSocket handling independent of simulation
- Database operations async with connection pooling
- Callback-based state broadcasting

## Frontend Architecture

### State Management (Zustand)

Single source of truth in `useTwinStore`:
- `currentState`: Latest motor state
- `alerts`: Active alerts
- `anomalies`: Detected anomalies
- `predictions`: Forecast data
- `historicalData`: Time-series data
- `connectionStatus`: WebSocket state
- `eventLog`: System events

### Component Hierarchy

```
App
├── Sidebar (Navigation)
└── MainContent
    ├── Dashboard
    │   ├── Header (ConnectionStatus)
    │   ├── MetricCards (5x2 grid)
    │   ├── MotorVisualization
    │   ├── Charts (RealTimeChart, MultiLineChart)
    │   ├── AlertPanel
    │   ├── PredictionPanel
    │   ├── ControlPanel
    │   ├── FaultInjectionPanel
    │   └── EventLog
    ├── Analytics
    ├── History
    └── Settings
```

### WebSocket Service

Singleton `WebSocketService` with:
- Automatic reconnection with exponential backoff
- Typed message handlers
- Connection state management
- Command queuing when disconnected

### Chart Components

Recharts-based components:
- `RealTimeChart`: Single metric time series
- `MultiLineChart`: Multiple metrics comparison
- `GaugeChart`/`HealthGauge`: Radial indicators
- `PredictionChart`: Forecast visualization

## Motor Physics Model

### Key Equations

**Speed Dynamics:**
```
acceleration = (target_speed - current_speed) * 0.5 * dt
speed += acceleration
```

**Torque:**
```
torque = rated_torque * (load/100) * (speed/rated_speed)
```

**Current:**
```
back_emf = back_emf_constant * speed / 1000
effective_voltage = voltage - back_emf
current = effective_voltage / stator_resistance * (load/100)
```

**Power:**
```
mechanical_power = torque * speed * 2π / 60000
electrical_power = voltage * current * √3 / 1000
efficiency = mechanical_power / electrical_power
```

**Temperature:**
```
heat_generated = current² * stator_resistance * dt * 0.1
cooling = cooling_coefficient * (temperature - 25) * dt
temperature += heat_generated - cooling
```

**Vibration:**
```
base_vibration = 0.5 + (speed/max_speed) * 1.0
load_vibration = (load/100) * 1.5
temp_vibration = max(0, (temperature - 80)/100) * 2.0
vibration = base + load + temp + noise
```

**Health Score:**
```
factors = [temp, vib, current, speed_dev, load, efficiency, fault]
weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
health_score = Σ(weight * factor)
```

## Anomaly Detection

### Rule-Based Rules

| Rule | Parameter | Condition | Threshold | Severity |
|------|-----------|-----------|-----------|----------|
| overtemperature_warning | temperature | > | 90°C | HIGH |
| overtemperature_critical | temperature | > | 110°C | CRITICAL |
| overcurrent_warning | current | > | 40A | HIGH |
| overcurrent_critical | current | > | 50A | CRITICAL |
| overspeed_warning | speed | > | 4500 RPM | HIGH |
| overspeed_critical | speed | > | 5000 RPM | CRITICAL |
| high_vibration_warning | vibration | > | 5 mm/s | MEDIUM |
| high_vibration_critical | vibration | > | 8 mm/s | CRITICAL |
| overload_warning | load | > | 90% | MEDIUM |
| undervoltage_warning | voltage | < | 300V | MEDIUM |
| low_efficiency_warning | efficiency | < | 70% | LOW |
| health_degraded | health_score | < | 50% | HIGH |

### ML Detection

- **Algorithm**: Isolation Forest (sklearn)
- **Features**: 15 normalized sensor readings
- **Contamination**: 5%
- **Training**: Requires 50+ normal samples
- **Integration**: Runs alongside rules, not replacement

## Prediction Models

### Simple Predictor (Default)
- Linear trend extrapolation
- 10-point sliding window
- Updates every simulation step
- No training required

### ML Predictor (Optional)
- Random Forest Regressor
- 12 input features
- 4 output targets (temp, vib, speed, health)
- 10-step horizon (10s intervals)
- Requires 100+ training samples

## Health Scoring

Multi-factor weighted scoring:

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Temperature | 25% | 100 - (temp/max_temp)*100 |
| Vibration | 20% | 100 - (vib/max_vib)*100 |
| Current | 15% | 100 - (current/max_current)*100 |
| Speed Deviation | 15% | 100 - (|target-speed|/target)*100 |
| Load | 10% | 100 - (load/100)*30 |
| Efficiency | 10% | efficiency * 100 |
| Fault State | 5% | 0 if fault, 100 if normal |

### Health Levels
- **90-100**: HEALTHY (Green)
- **75-89**: GOOD (Light Green)
- **50-74**: WARNING (Orange)
- **25-49**: CRITICAL (Red)
- **0-24**: FAILURE (Dark Red)

## Database Schema

### Tables

**motor_states**: Time-series sensor data
**anomalies**: Detected anomalies with metadata
**alerts**: User-facing alerts
**commands**: Executed commands audit trail
**predictions**: Forecast records
**system_events**: General event log

### Retention Policy

- Live data: 1000 points in memory
- Database: Configurable (default 30 days)
- Cleanup: Automatic via HistoryService

## Security

### Input Validation
- All REST endpoints use Pydantic models
- WebSocket commands validated before execution
- Numeric ranges enforced
- NaN/Infinity rejected

### CORS
- Configurable origins
- Restricted in production

### WebSocket
- Command acknowledgment
- No sensitive data in messages
- Graceful reconnection

## Scalability Considerations

### Current Limitations
- Single simulation instance
- In-memory WebSocket connections
- SQLite for development

### Production Scaling
- Multiple backend instances with shared PostgreSQL
- Redis for WebSocket pub/sub
- Load balancer for HTTP/WebSocket
- Separate ML inference service
- Time-series database (InfluxDB/TimescaleDB)

## Monitoring

### Health Endpoint
```json
{
  "status": "healthy",
  "simulation_running": true,
  "database": "connected",
  "websocket_clients": 1,
  "uptime_seconds": 3600
}
```

### Logging
Structured JSON logs with:
- Request/response tracing
- Simulation metrics
- Anomaly events
- Error tracking

## Testing Strategy

### Backend
- Unit tests for motor physics
- Anomaly detection rules
- API endpoint integration
- WebSocket communication
- Simulation engine lifecycle

### Frontend
- Component rendering
- Store state management
- Hook behavior
- WebSocket integration

## Deployment Architecture

```
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │ HTTPS/WSS
                           ▼
                    ┌─────────────┐
                    │   Nginx     │ ◄── Reverse Proxy, SSL, Static Files
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌─────────────┐           ┌─────────────┐
       │  Frontend   │           │  Backend    │
       │  (Nginx)    │           │  (FastAPI)  │
       └─────────────┘           └──────┬──────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              ┌──────────┐       ┌──────────┐       ┌──────────┐
              │PostgreSQL│       │  Redis   │       │  ML Svc  │
              └──────────┘       └──────────┘       └──────────┘
```