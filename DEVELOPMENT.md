# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker (optional)

### Environment Setup

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
cp .env.example .env
# Edit .env as needed

uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Verify Installation

- Backend: http://localhost:8000/api/health
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Project Structure Details

### Backend Module Organization

```
app/
├── api/           # HTTP & WebSocket endpoints
├── core/          # Config, logging, security
├── twin/          # Digital twin simulation
├── anomaly/       # Anomaly detection
├── prediction/    # Predictive analytics
├── database/      # ORM, repositories
├── services/      # Business logic
├── schemas/       # Pydantic models
└── tests/         # Unit tests
```

### Frontend Module Organization

```
src/
├── components/    # Reusable UI components
├── pages/         # Page-level components
├── services/      # API & WebSocket clients
├── hooks/         # Custom React hooks
├── store/         # Zustand state
├── types/         # TypeScript interfaces
└── utils/         # Helpers
```

## Development Workflow

### Adding New Motor Parameters

1. Update `MotorParameters` in `app/twin/parameters.py`
2. Update `MotorConfig` schema in `app/schemas/motor.py`
3. Update frontend types in `src/types/twin.ts`
4. Modify `MotorModel` physics if needed
5. Add validation in API routes

### Adding New Anomaly Rules

1. Add rule to `DEFAULT_RULES` in `app/anomaly/rules.py`
2. Or dynamically via API: `rule_engine.add_rule()`
3. Rule format:
```python
AnomalyRule(
    name="unique_name",
    parameter="temperature",  # or current, speed, etc.
    condition=">",            # >, <, >=, <=, ==
    threshold=95.0,
    severity=AnomalySeverity.HIGH,
    description="Description"
)
```

### Adding New Prediction Models

1. Implement in `app/prediction/models.py`
2. Register in `PredictionEngine` in `app/prediction/predictor.py`
3. Add training script in `ml/`
4. Save model to `models/` directory

### Adding New API Endpoints

1. Define Pydantic schemas in `app/schemas/`
2. Add route in `app/api/routes.py`
3. Include router in `app/api/__init__.py`
4. Update frontend API service in `src/services/api.ts`

### Adding New Frontend Components

1. Create component in `src/components/`
2. Export from category index
3. Use in pages
4. Add styles to `App.css`

## Code Style

### Python

- Type hints required
- Pydantic models for validation
- Docstrings for public functions
- Async/await for I/O
- Max line length: 100 chars

```python
async def get_motor_state(motor_id: str) -> MotorState:
    """Retrieve current motor state."""
    ...
```

### TypeScript

- Strict mode enabled
- No `any` unless necessary
- Interface over type for objects
- Functional components with hooks

```typescript
interface MotorState {
  timestamp: number;
  speed: number;
  // ...
}
```

## Testing

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose
pytest -k "test_motor"    # Filter by name
pytest --cov=app          # Coverage
```

### Frontend Tests

```bash
cd frontend
npm test                  # Run tests
npm run test:ui           # Vitest UI
```

### Test Organization

- `test_motor_model.py` - Physics simulation
- `test_anomaly_detection.py` - Rules & ML
- `test_api.py` - REST endpoints
- `test_simulation_engine.py` - Async engine
- `components.test.tsx` - UI components
- `hooks.test.ts` - Custom hooks

## Debugging

### Backend Debugging

1. Add breakpoints in VS Code
2. Launch config:
```json
{
  "type": "python",
  "request": "launch",
  "module": "uvicorn",
  "args": ["app.main:app", "--reload"],
  "console": "integratedTerminal"
}
```

### Frontend Debugging

1. React DevTools browser extension
2. Redux DevTools for Zustand (optional)
3. VS Code debugger for TypeScript

### WebSocket Debugging

```bash
# CLI test
wscat -c ws://localhost:8000/ws/twin
```

### Database Inspection

```bash
# SQLite
sqlite3 digital_twin.db ".schema"
sqlite3 digital_twin.db "SELECT * FROM motor_states LIMIT 5;"

# PostgreSQL
psql -h localhost -U postgres -d digital_twin
```

## Common Tasks

### Reset Database

```bash
cd backend
rm digital_twin.db
uvicorn app.main:app --reload  # Recreates tables
```

### Train ML Models

```bash
cd backend/ml
python data_generator.py
python train_anomaly.py
python train_prediction.py
```

### Update Dependencies

```bash
# Backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Frontend
npm update
npm audit fix
```

### Code Formatting

```bash
# Backend
pip install black isort
black app/
isort app/

# Frontend
npx prettier --write src/
```

## Performance Profiling

### Backend

```python
# Add to simulation loop
import cProfile
profiler = cProfile.Profile()
profiler.enable()
# ... simulation ...
profiler.disable()
profiler.print_stats(sort='cumulative')
```

### Frontend

- Chrome DevTools Performance tab
- React Profiler
- Check re-renders with `why-did-you-render`

## Troubleshooting

### WebSocket Connection Fails

1. Check CORS in backend config
2. Verify proxy in `vite.config.ts`
3. Check firewall/antivirus
4. Try `ws://localhost:8000/ws/twin` directly

### Database Errors

1. Verify `DATABASE_URL` format
2. Check permissions on SQLite file
3. For PostgreSQL: verify connection string

### Simulation Not Updating

1. Check `simulation_engine.running`
2. Verify callback registration
3. Check WebSocket message handler

### ML Model Not Loading

1. Check `models/` directory exists
2. Verify model file names match
3. Check scikit-learn version compatibility

## Git Workflow

### Branch Strategy

- `main` - Production ready
- `develop` - Integration branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation

### Commit Messages

```
feat: add new anomaly detection rule
fix: correct temperature calculation
docs: update API documentation
test: add motor model unit tests
refactor: simplify prediction engine
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## IDE Configuration

### VS Code Extensions

- Python
- Pylance
- TypeScript/React
- ESLint
- Prettier
- Docker
- GitLens

### Settings.json

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest
  
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: { node-version: '20' }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run build
      - run: cd frontend && npm test
```

## Useful Commands

```bash
# View logs
docker compose logs -f backend

# Execute in container
docker compose exec backend bash

# Database migration
cd backend && alembic upgrade head

# Create migration
cd backend && alembic revision --autogenerate -m "description"

# Frontend production build
cd frontend && npm run build
```