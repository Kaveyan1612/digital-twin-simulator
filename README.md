# Digital Twin Web Simulator

A production-quality digital twin simulator for an electric motor system, built with React + TypeScript + FastAPI + WebSockets.

## Features

- **Real-time Simulation**: 10 Hz internal simulation with 5 Hz WebSocket updates
- **Physics-based Motor Model**: Realistic relationships between speed, torque, current, temperature, vibration, and efficiency
- **WebSocket Communication**: Live bidirectional communication between frontend and backend
- **Interactive Controls**: Start/stop motor, set target speed, load, voltage, operating modes
- **Fault Injection**: Test anomaly detection with overtemperature, overcurrent, high vibration, overspeed, undervoltage, overload, sensor anomalies
- **Rule-based Anomaly Detection**: Configurable thresholds for all critical parameters
- **ML-based Anomaly Detection**: Isolation Forest for detecting complex anomalous patterns
- **Predictive Analytics**: Forecast temperature, vibration, speed, and health score
- **Predictive Warnings**: Early warnings before thresholds are breached
- **Health Scoring**: Multi-factor health assessment (temperature, vibration, current, speed deviation, load, efficiency, faults)
- **Real-time Charts**: Live updating charts for all motor parameters
- **Historical Data**: Persistent storage with configurable retention
- **Analytics Dashboard**: Statistical analysis and historical visualization
- **Event Logging**: Complete audit trail of all system events
- **Docker Support**: Production-ready containerization
- **Comprehensive Tests**: Backend and frontend unit tests

## Architecture

```
┌─────────────┐     WebSocket      ┌──────────────┐
│   React     │ ◄────────────────► │   FastAPI    │
│  Frontend   │                    │   Backend    │
└─────────────┘                    └──────┬───────┘
                                          │
           ┌──────────────────────────────┼──────────────────────────────┐
           │                              │                              │
           ▼                              ▼                              ▼
    ┌─────────────┐               ┌─────────────┐               ┌─────────────┐
    │  Digital    │               │  Anomaly    │               │ Prediction  │
    │  Twin       │               │  Detection  │               │  Engine     │
    │  Engine     │               │  (Rules+ML) │               │             │
    └──────┬──────┘               └──────┬──────┘               └──────┬──────┘
           │                              │                              │
           ▼                              ▼                              ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                        Database (SQLite/PostgreSQL)                     │
    │  Motor States │ Anomalies │ Alerts │ Commands │ Predictions │ Events   │
    └─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### Docker Deployment

```bash
# Production
docker compose up --build

# Development
docker compose -f docker-compose.dev.yml up --build
```

## Technology Stack

### Frontend
- React 18 + TypeScript
- Vite for build tooling
- Recharts for visualizations
- Zustand for state management
- Axios for REST API
- Native WebSocket API

### Backend
- Python 3.11+
- FastAPI for REST API and WebSockets
- SQLModel for database ORM
- NumPy/SciPy for numerical computation
- scikit-learn for ML anomaly detection
- Pydantic for validation
- Uvicorn ASGI server

### Database
- Development: SQLite
- Production: PostgreSQL
- SQLAlchemy/SQLModel ORM

## Project Structure

```
digital-twin-simulator/
├── backend/
│   ├── app/
│   │   ├── api/           # REST API & WebSocket routes
│   │   ├── core/          # Configuration & logging
│   │   ├── twin/          # Digital twin engine
│   │   │   ├── motor_model.py    # Physics simulation
│   │   │   ├── engine.py         # Async simulation loop
│   │   │   ├── state.py          # Twin state management
│   │   │   ├── parameters.py     # Motor parameters
│   │   │   └── faults.py         # Fault injection
│   │   ├── anomaly/       # Anomaly detection
│   │   │   ├── detector.py       # Main detector
│   │   │   ├── rules.py          # Rule-based detection
│   │   │   ├── features.py       # Feature extraction
│   │   │   └── model.py          # ML model (Isolation Forest)
│   │   ├── prediction/    # Predictive analytics
│   │   │   ├── predictor.py      # Main prediction engine
│   │   │   ├── features.py       # Prediction features
│   │   │   └── models.py         # ML models
│   │   ├── database/      # Database models & repositories
│   │   ├── services/      # Business logic services
│   │   ├── schemas/       # Pydantic models
│   │   └── tests/         # Unit tests
│   ├── ml/                # ML training pipeline
│   ├── models/            # Trained model artifacts
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Dashboard/
│   │   │   ├── Charts/
│   │   │   ├── Controls/
│   │   │   ├── Alerts/
│   │   │   ├── Motor/
│   │   │   ├── Predictions/
│   │   │   └── Common/
│   │   ├── pages/         # Page components
│   │   ├── services/      # API & WebSocket services
│   │   ├── hooks/         # Custom React hooks
│   │   ├── store/         # Zustand store
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

## API Endpoints

### Health
- `GET /api/health` - System health check

### Digital Twin
- `GET /api/twin/state` - Current motor state
- `GET /api/twin/config` - Motor configuration
- `POST /api/twin/start` - Start motor
- `POST /api/twin/stop` - Stop motor
- `POST /api/twin/reset` - Reset motor
- `POST /api/twin/emergency-stop` - Emergency stop
- `POST /api/twin/target-speed` - Set target speed
- `POST /api/twin/load` - Set load
- `POST /api/twin/voltage` - Set voltage
- `POST /api/twin/operating-mode` - Set operating mode
- `POST /api/twin/inject-fault` - Inject fault
- `POST /api/twin/clear-fault` - Clear fault
- `GET /api/twin/history` - Historical data
- `GET /api/twin/statistics` - Statistics

### WebSocket
- `WS /ws/twin` - Real-time state stream

## WebSocket Messages

### Outgoing (Server → Client)
```json
{
  "type": "twin_state",
  "timestamp": 1720000000,
  "data": { ...MotorState }
}
```

```json
{
  "type": "anomaly",
  "timestamp": 1720000000,
  "data": { ...AnomalyResult }
}
```

```json
{
  "type": "prediction",
  "timestamp": 1720000000,
  "data": { ...PredictionResult }
}
```

```json
{
  "type": "alert",
  "timestamp": 1720000000,
  "data": { ...AlertInfo }
}
```

### Incoming (Client → Server)
```json
{ "type": "set_target_speed", "value": 3500 }
```
```json
{ "type": "set_load", "value": 75 }
```
```json
{ "type": "start_motor" }
```
```json
{ "type": "inject_fault", "fault": "overtemperature" }
```

## Configuration

Environment variables (backend/.env):

```env
APP_ENV=development
DATABASE_URL=sqlite:///./digital_twin.db
SIMULATION_FREQUENCY=10
WEBSOCKET_UPDATE_RATE=5
MAX_SPEED=5000
MAX_TEMPERATURE=120
MAX_CURRENT=50
MAX_VIBRATION=10
MOTOR_ID=MOTOR-001
ANOMALY_DETECTION_ENABLED=true
ML_ANOMALY_DETECTION_ENABLED=true
PREDICTION_ENABLED=true
LIVE_HISTORY_POINTS=1000
DATABASE_RETENTION_DAYS=30
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Demonstration Scenario

1. Open dashboard at http://localhost:5173
2. Click **START** - motor begins accelerating
3. Set **Target Speed** to 3000 RPM, **Load** to 40%
4. Observe real-time parameters stabilize
5. Increase **Load** to 80% - watch current, torque, temperature rise
6. Click **Overtemperature** fault - temperature climbs rapidly
7. Anomaly detector triggers **HIGH TEMPERATURE** alert
8. Prediction engine forecasts temperature exceeding 110°C in 60s
9. **PREDICTIVE WARNING** appears
10. Click **CLEAR FAULT** and reduce load - system recovers
11. View **Analytics** and **History** pages for recorded data

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## ML Pipeline

The ML anomaly detector uses Isolation Forest trained on normal operating data:

```bash
cd backend/ml
python train_anomaly.py
```

Models are saved to `backend/models/` and loaded automatically on startup.

## Production Deployment

1. Set `APP_ENV=production`
2. Configure PostgreSQL in `DATABASE_URL`
3. Set secure `CORS_ORIGINS`
4. Use reverse proxy (nginx) with SSL
5. Run with `docker compose up --build`

## License

MIT License - see LICENSE file for details.