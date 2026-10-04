# Testing Documentation

## Overview

This document describes the testing strategy, test organization, and how to run tests for the Digital Twin Simulator.

## Test Pyramid

```
         /\
        /  \     E2E Tests (Few)
       /----\    
      /      \   Integration Tests (Some)
     /--------\  
    /          \ Unit Tests (Many)
   /____________\
```

### Unit Tests (70%)
- Fast, isolated, no external dependencies
- Test individual functions/classes
- Mock all external calls

### Integration Tests (20%)
- Test component interactions
- Real database (test instance)
- Real WebSocket connections

### End-to-End Tests (10%)
- Full user workflows
- Browser automation
- Production-like environment

## Backend Testing

### Test Structure

```
backend/app/tests/
├── test_motor_model.py          # Physics simulation tests
├── test_anomaly_detection.py    # Rule & ML detection tests
├── test_api.py                  # REST API tests
├── test_simulation_engine.py    # Async engine tests
└── conftest.py                  # Pytest fixtures
```

### Running Tests

```bash
cd backend

# All tests
pytest

# Verbose
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest app/tests/test_motor_model.py

# Specific test
pytest app/tests/test_motor_model.py::test_motor_start

# Parallel (requires pytest-xdist)
pytest -n auto

# Watch mode
pytest --watch
```

### Test Categories

#### Motor Model Tests (`test_motor_model.py`)

```python
# Physics validation
test_motor_initial_state()
test_motor_start()
test_motor_stop()
test_motor_emergency_stop()
test_motor_reset()
test_target_speed_change()
test_load_change()
test_voltage_change()

# Physical relationships
test_temperature_responds_to_load()
test_current_responds_to_load()
test_vibration_responds_to_abnormal_conditions()

# Fault injection
test_fault_injection_overtemperature()
test_fault_injection_overcurrent()
test_fault_injection_high_vibration()
test_fault_injection_overspeed()
test_fault_injection_undervoltage()
test_fault_injection_overload()
test_clear_fault()

# Health scoring
test_health_score_calculation()
test_health_score_degraded_with_fault()

# State serialization
test_motor_state_dict()
```

#### Anomaly Detection Tests (`test_anomaly_detection.py`)

```python
# Rule engine
test_rule_engine_normal_state()
test_rule_engine_overtemperature_warning()
test_rule_engine_overtemperature_critical()
test_rule_engine_overcurrent_warning()
test_rule_engine_overspeed_warning()
test_rule_engine_high_vibration_warning()
test_rule_engine_persistent_speed_deviation()

# Integration
test_anomaly_detector_integration()
test_anomaly_severity_ranking()

# Configuration
test_default_rules_exist()
test_add_remove_rule()
```

#### API Tests (`test_api.py`)

```python
# Health
test_health_endpoint()

# State
test_twin_state_endpoint()
test_twin_config_endpoint()

# Control
test_start_motor_endpoint()
test_stop_motor_endpoint()
test_reset_motor_endpoint()
test_emergency_stop_endpoint()
test_set_target_speed_endpoint()
test_set_load_endpoint()
test_set_voltage_endpoint()
test_set_operating_mode_endpoint()
test_inject_fault_endpoint()
test_clear_fault_endpoint()

# History
test_history_endpoint()
test_statistics_endpoint()

# Documentation
test_docs_endpoint()
```

#### Simulation Engine Tests (`test_simulation_engine.py`)

```python
test_simulation_engine_start_stop()
test_simulation_engine_updates_motor()
test_simulation_callback()
test_digital_twin_integration()
test_digital_twin_controls()
test_digital_twin_fault_injection()
test_digital_twin_emergency_stop()
test_digital_twin_reset()
```

### Test Fixtures (`conftest.py`)

```python
@pytest.fixture
def motor_params():
    return MotorParameters()

@pytest.fixture
def motor_model(motor_params):
    return MotorModel(motor_params)

@pytest.fixture
def normal_state():
    return MotorState(...)

@pytest.fixture
def overtemperature_state():
    return MotorState(temperature=95, ...)

@pytest.fixture
def client():
    return TestClient(app)
```

### Mocking Guidelines

```python
# Mock database
@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

# Mock WebSocket
@pytest.fixture
def mock_websocket():
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    return ws

# Mock time
@pytest.fixture(autouse=True)
def mock_time(monkeypatch):
    monkeypatch.setattr(time, 'time', lambda: 1720000000.0)
```

## Frontend Testing

### Test Structure

```
frontend/src/tests/
├── setup.ts                 # Test setup & mocks
├── components.test.tsx      # Component tests
├── hooks.test.ts            # Hook tests
└── utils.test.ts            # Utility tests
```

### Running Tests

```bash
cd frontend

# All tests
npm test

# Watch mode
npm test -- --watch

# UI mode
npm test -- --ui

# Coverage
npm test -- --coverage
```

### Test Setup (`setup.ts`)

```typescript
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Zustand
vi.mock('zustand', () => ({
  create: (fn) => { ... }
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
```

### Component Tests (`components.test.tsx`)

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MetricCard, StatusBadge, ConnectionStatus } from '../components/Common';

describe('MetricCard', () => {
  test('renders title and value correctly', () => {
    render(<MetricCard title="TEMPERATURE" value={67.4} unit="°C" />);
    expect(screen.getByText('TEMPERATURE')).toBeInTheDocument();
  });

  test('renders with status color', () => {
    render(<MetricCard title="STATUS" value="RUNNING" status="RUNNING" />);
    // Check border color
  });

  test('renders health label', () => {
    render(<MetricCard title="HEALTH" value={94} unit="%" healthScore={94} />);
    expect(screen.getByText('HEALTHY')).toBeInTheDocument();
  });
});

describe('StatusBadge', () => {
  test('renders with severity color', () => {
    render(<StatusBadge label="HIGH" severity="HIGH" />);
    // Check styles
  });
});

describe('ConnectionStatus', () => {
  test('shows connected status', () => {
    render(<ConnectionStatus status="connected" />);
    expect(screen.getByText('CONNECTED')).toBeInTheDocument();
  });
});
```

### Hook Tests (`hooks.test.ts`)

```typescript
import { renderHook, act } from '@testing-library/react';
import { useTwinStore } from '../store/twinStore';

describe('useTwinStore', () => {
  beforeEach(() => {
    act(() => {
      useTwinStore.getState().setCurrentState(null);
      useTwinStore.getState().clearAlerts();
      // ... reset all
    });
  });

  test('sets and gets current state', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.setCurrentState(mockState);
    });
    
    expect(result.current.currentState).toEqual(mockState);
  });

  test('adds and retrieves alerts', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addAlert(mockAlert);
    });
    
    expect(result.current.alerts).toHaveLength(1);
  });

  test('limits history size', () => {
    const { result } = renderHook(() => useTwinStore());
    const largeHistory = Array(1500).fill(mockState);
    
    act(() => {
      result.current.setHistoricalData(largeHistory);
    });
    
    expect(result.current.historicalData.length).toBeLessThanOrEqual(1000);
  });
});
```

## End-to-End Testing

### Cypress Setup

```bash
cd frontend
npm install -D cypress
npx cypress open
```

### E2E Test Scenarios

```javascript
// cypress/e2e/dashboard.cy.js
describe('Dashboard', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
    cy.waitForWebSocket();
  });

  it('displays motor metrics', () => {
    cy.get('.metric-card').should('have.length', 10);
    cy.contains('SPEED').should('be.visible');
    cy.contains('TEMPERATURE').should('be.visible');
  });

  it('starts motor on button click', () => {
    cy.contains('START').click();
    cy.get('.metric-card').contains('RUNNING').should('be.visible');
  });

  it('changes target speed', () => {
    cy.contains('START').click();
    cy.get('input[type="range"]').first().invoke('val', 3000).trigger('change');
    cy.contains('3000 RPM').should('be.visible');
  });

  it('injects fault and shows anomaly', () => {
    cy.contains('START').click();
    cy.contains('Overtemperature').click();
    cy.contains('ANOMALY: OVERTEMPERATURE').should('be.visible');
  });

  it('shows predictive warning', () => {
    cy.contains('START').click();
    cy.contains('Overtemperature').click();
    cy.contains('PREDICTIVE WARNING').should('be.visible');
  });
});
```

### WebSocket Testing Helper

```javascript
// cypress/support/commands.js
Cypress.Commands.add('waitForWebSocket', () => {
  cy.window().then((win) => {
    return new Cypress.Promise((resolve) => {
      const check = () => {
        if (win.websocketService?.isConnected()) {
          resolve();
        } else {
          setTimeout(check, 100);
        }
      };
      check();
    });
  });
});
```

## Test Data Management

### Test Database

```python
# pytest fixture for test database
@pytest.fixture(scope="session")
def test_db():
    engine = create_engine("sqlite:///./test.db")
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
```

### Test Data Factories

```python
# factories.py
def create_motor_state(**overrides):
    defaults = {
        "timestamp": time.time(),
        "motor_id": "TEST-MOTOR",
        "running": True,
        "speed": 3000,
        "temperature": 60,
        # ...
    }
    return MotorState(**{**defaults, **overrides})

def create_anomaly(**overrides):
    defaults = {
        "anomaly_type": "OVERTEMPERATURE",
        "severity": "HIGH",
        "confidence": 1.0,
        # ...
    }
    return AnomalyResult(**{**defaults, **overrides})
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run test -- --run
      - run: cd frontend && npm run build

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: docker compose -f docker-compose.test.yml up -d
      - run: sleep 30
      - run: cd frontend && npx cypress run
      - run: docker compose -f docker-compose.test.yml down
```

### Test Docker Compose

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - APP_ENV=test
      - DATABASE_URL=sqlite:///./test.db
    ports:
      - "8001:8000"
  
  frontend:
    build: ./frontend
    ports:
      - "5174:80"
```

## Code Coverage Targets

| Component | Target |
|-----------|--------|
| Motor Model | 90% |
| Anomaly Detection | 85% |
| Prediction Engine | 80% |
| API Endpoints | 85% |
| Simulation Engine | 75% |
| Frontend Components | 70% |
| Frontend Hooks | 80% |
| Overall | 80% |

## Performance Testing

### Load Testing (Locust)

```python
# locustfile.py
from locust import HttpUser, task, between

class DigitalTwinUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.client.get("/api/health")
    
    @task(10)
    def get_state(self):
        self.client.get("/api/twin/state")
    
    @task(3)
    def get_history(self):
        self.client.get("/api/twin/history?hours=1")
    
    @task(1)
    def set_speed(self):
        self.client.post("/api/twin/target-speed", json={"value": 3000})
```

```bash
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### WebSocket Load Testing

```python
# ws_locust.py
from locust import User, task, between
import websocket
import json

class WebSocketUser(User):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        self.ws = websocket.create_connection("ws://localhost:8000/ws/twin")
    
    @task
    def receive_messages(self):
        for _ in range(10):
            self.ws.recv()
    
    def on_stop(self):
        self.ws.close()
```

## Test Debugging

### Backend

```bash
# Debug specific test
pytest app/tests/test_motor_model.py::test_motor_start -v --pdb

# Print test output
pytest -s

# Verbose with traceback
pytest -vv --tb=long
```

### Frontend

```bash
# Debug in browser
npm test -- --ui

# Single test file
npm test -- components.test.tsx

# Update snapshots
npm test -- -u
```

## Common Testing Patterns

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### WebSocket Testing

```python
@pytest.mark.asyncio
async def test_websocket_flow():
    async with websockets.connect("ws://localhost:8000/ws/twin") as ws:
        # Send command
        await ws.send(json.dumps({"type": "set_target_speed", "value": 3000}))
        
        # Receive ack
        ack = await ws.recv()
        assert json.loads(ack)["type"] == "command_ack"
        
        # Receive state
        state = await ws.recv()
        data = json.loads(state)
        assert data["type"] == "twin_state"
```

### Time-Based Testing

```python
@pytest.fixture(autouse=True)
def freeze_time(monkeypatch):
    import time
    frozen = 1720000000.0
    monkeypatch.setattr(time, 'time', lambda: frozen)
```

## Test Reporting

### JUnit XML

```bash
pytest --junitxml=report.xml
```

### HTML Coverage

```bash
pytest --cov=app --cov-report=html:coverage_html
open coverage_html/index.html
```

### Allure Reports

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## Test Maintenance

### Adding New Tests

1. Identify what needs testing
2. Choose appropriate test level
3. Create test file or add to existing
4. Use fixtures for common setup
5. Run and verify

### Flaky Test Handling

```python
# Retry flaky tests
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_flaky_network_call():
    ...
```

### Test Data Cleanup

```python
@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield
    # Cleanup after each test
    TestMotorState.query.delete()
    TestAnomaly.query.delete()
```

## Best Practices

1. **Test behavior, not implementation**
2. **One assertion per test** (when possible)
3. **Descriptive test names**: `test_<what>_<when>_<expected>`
4. **Isolate tests** - no shared state
5. **Fast unit tests** - < 100ms each
6. **Realistic integration tests** - use real DB
7. **Meaningful E2E tests** - critical user paths
8. **Mock at boundaries** - database, network, time
9. **Test edge cases** - boundaries, errors, empty states
10. **Keep tests maintainable** - refactor with code