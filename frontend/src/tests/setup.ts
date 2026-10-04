import '@testing-library/jest-dom';
import { vi } from 'vitest';

const initialState = {
  currentState: null,
  alerts: [],
  anomalies: [],
  predictions: {},
  historicalData: [],
  statistics: null,
  connectionStatus: 'disconnected',
  eventLog: [],
};

const mockSetState = vi.fn((partial) => {
  const newState = typeof partial === 'function' ? partial(global.__testState) : partial;
  global.__testState = { ...global.__testState, ...newState };
});

const mockGetState = vi.fn(() => {
  return global.__testState;
});

global.__testState = {
  currentState: null,
  alerts: [],
  anomalies: [],
  predictions: {},
  historicalData: [],
  statistics: null,
  connectionStatus: 'disconnected',
  eventLog: [],
  setCurrentState: vi.fn((s) => global.__testState.setCurrentState && global.__testState.setCurrentState(s)),
  addAlert: vi.fn((a) => {
    const prev = global.__testState;
    const exists = prev.alerts.some((al) => al.id === a.id);
    if (!exists) {
      global.__testState.alerts = [a, ...prev.alerts].slice(0, 100);
    }
  }),
  clearAlerts: vi.fn(() => { global.__testState.alerts = []; }),
  acknowledgeAlert: vi.fn((id) => {
    global.__testState.alerts = global.__testState.alerts.map((a) => a.id === id ? { ...a, acknowledged: true } : a);
  }),
  addAnomaly: vi.fn((a) => {
    global.__testState.anomalies = [a, ...global.__testState.anomalies].slice(0, 100);
  }),
  clearAnomalies: vi.fn(() => { global.__testState.anomalies = []; }),
  setPredictions: vi.fn((type, p) => {
    global.__testState.predictions = { ...global.__testState.predictions, [type]: p };
  }),
  setHistoricalData: vi.fn((d) => { global.__testState.historicalData = d.slice(-1000); }),
  setStatistics: vi.fn((s) => { global.__testState.statistics = s; }),
  setConnectionStatus: vi.fn((s) => { global.__testState.connectionStatus = s; }),
  addEvent: vi.fn((e) => { global.__testState.eventLog = [e, ...global.__testState.eventLog].slice(0, 200); }),
  clearEventLog: vi.fn(() => { global.__testState.eventLog = []; }),
};

const mockStore = {
  getState: vi.fn(() => global.__testState),
  setState: vi.fn((partial) => {
    const newState = typeof partial === 'function' ? partial(global.__testState) : partial;
    global.__testState = { ...global.__testState, ...newState };
  }),
  subscribe: vi.fn(() => () => {}),
};

vi.mock('zustand', () => ({
  create: vi.fn(() => {
    const hook = (selector) => {
      if (typeof selector === 'function') {
        return selector(global.__testState);
      }
      return global.__testState;
    };
    hook.getState = global.__testState;
    hook.setState = (partial) => {
      const newState = typeof partial === 'function' ? partial(global.__testState) : partial;
      global.__testState = { ...global.__testState, ...newState };
    };
    hook.subscribe = vi.fn(() => () => {});
    return hook;
  }),
}));

vi.mock('../services/websocket', () => ({
  websocketService: {
    onState: vi.fn(() => vi.fn()),
    onAnomaly: vi.fn(() => vi.fn()),
    onPrediction: vi.fn(() => vi.fn()),
    onAlert: vi.fn(() => vi.fn()),
    onConnectionChange: vi.fn(() => vi.fn()),
    connect: vi.fn(),
    disconnect: vi.fn(),
    sendCommand: vi.fn(),
    isConnected: vi.fn(() => true),
  },
}));

global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

beforeEach(() => {
  global.__testState = {
    currentState: null,
    alerts: [],
    anomalies: [],
    predictions: {},
    historicalData: [],
    statistics: null,
    connectionStatus: 'disconnected',
    eventLog: [],
    setCurrentState: vi.fn((s) => { global.__testState.currentState = s; }),
    addAlert: vi.fn((a) => {
      const prev = global.__testState;
      const exists = prev.alerts.some((al) => al.id === a.id);
      if (!exists) {
        global.__testState.alerts = [a, ...prev.alerts].slice(0, 100);
      }
    }),
    clearAlerts: vi.fn(() => { global.__testState.alerts = []; }),
    acknowledgeAlert: vi.fn((id) => {
      global.__testState.alerts = global.__testState.alerts.map((a) => a.id === id ? { ...a, acknowledged: true } : a);
    }),
    addAnomaly: vi.fn((a) => {
      global.__testState.anomalies = [a, ...global.__testState.anomalies].slice(0, 100);
    }),
    clearAnomalies: vi.fn(() => { global.__testState.anomalies = []; }),
    setPredictions: vi.fn((type, p) => {
      global.__testState.predictions = { ...global.__testState.predictions, [type]: p };
    }),
    setHistoricalData: vi.fn((d) => { global.__testState.historicalData = d.slice(-1000); }),
    setStatistics: vi.fn((s) => { global.__testState.statistics = s; }),
    setConnectionStatus: vi.fn((s) => { global.__testState.connectionStatus = s; }),
    addEvent: vi.fn((e) => { global.__testState.eventLog = [e, ...global.__testState.eventLog].slice(0, 200); }),
    clearEventLog: vi.fn(() => { global.__testState.eventLog = []; }),
  };
});