import { create } from 'zustand';
import type { MotorState, AlertInfo, HistoricalDataPoint, StatisticsResponse, AnomalyResult } from '../types/twin';

interface PredictionData {
  prediction_type: string;
  current_value: number;
  predictions: Array<{ time: number; value: number; ml_value?: number }>;
  warning?: string;
  warning_threshold?: number;
}

interface TwinState {
  currentState: MotorState | null;
  alerts: AlertInfo[];
  anomalies: AnomalyResult[];
  predictions: Record<string, PredictionData>;
  historicalData: HistoricalDataPoint[];
  statistics: StatisticsResponse | null;
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  eventLog: Array<{ timestamp: number; message: string; type: string }>;
  setCurrentState: (state: MotorState) => void;
  addAlert: (alert: AlertInfo) => void;
  clearAlerts: () => void;
  acknowledgeAlert: (id: number) => void;
  addAnomaly: (anomaly: AnomalyResult) => void;
  clearAnomalies: () => void;
  setPredictions: (type: string, predictions: PredictionData) => void;
  setHistoricalData: (data: HistoricalDataPoint[]) => void;
  setStatistics: (stats: StatisticsResponse) => void;
  setConnectionStatus: (status: 'connected' | 'disconnected' | 'connecting') => void;
  addEvent: (event: { timestamp: number; message: string; type: string }) => void;
  clearEventLog: () => void;
}

const MAX_HISTORY = 1000;
const MAX_ALERTS = 100;
const MAX_ANOMALIES = 100;
const MAX_EVENTS = 200;

export const useTwinStore = create<TwinState>((set) => ({
  currentState: null,
  alerts: [],
  anomalies: [],
  predictions: {},
  historicalData: [],
  statistics: null,
  connectionStatus: 'disconnected',
  eventLog: [],

  setCurrentState: (state) => set({ currentState: state }),

  addAlert: (alert) => set((prev) => {
    const exists = prev.alerts.some(a => a.id === alert.id);
    if (exists) return prev;
    const newAlerts = [alert, ...prev.alerts].slice(0, MAX_ALERTS);
    return { alerts: newAlerts };
  }),

  clearAlerts: () => set({ alerts: [] }),

  acknowledgeAlert: (id) => set((prev) => ({
    alerts: prev.alerts.map(a => a.id === id ? { ...a, acknowledged: true } : a)
  })),

  addAnomaly: (anomaly) => set((prev) => {
    const newAnomalies = [anomaly, ...prev.anomalies].slice(0, MAX_ANOMALIES);
    return { anomalies: newAnomalies };
  }),

  clearAnomalies: () => set({ anomalies: [] }),

  setPredictions: (type, predictions) => set((prev) => ({
    predictions: { ...prev.predictions, [type]: predictions }
  })),

  setHistoricalData: (data) => set({ historicalData: data.slice(-MAX_HISTORY) }),

  setStatistics: (stats) => set({ statistics: stats }),

  setConnectionStatus: (status) => set({ connectionStatus: status }),

  addEvent: (event) => set((prev) => {
    const newEvents = [event, ...prev.eventLog].slice(0, MAX_EVENTS);
    return { eventLog: newEvents };
  }),

  clearEventLog: () => set({ eventLog: [] }),
}));