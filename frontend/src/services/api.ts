import axios from 'axios';
import type {
  MotorState,
  MotorConfig,
  CommandResponse,
  HistoricalDataPoint,
  StatisticsResponse,
  HealthResponse,
} from '../types/twin';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function getHealth(): Promise<HealthResponse> {
  const response = await api.get('/health');
  return response.data;
}

export async function getCurrentState(): Promise<MotorState> {
  const response = await api.get('/twin/state');
  return response.data;
}

export async function getConfig(): Promise<MotorConfig> {
  const response = await api.get('/twin/config');
  return response.data;
}

export async function startMotor(): Promise<CommandResponse> {
  const response = await api.post('/twin/start');
  return response.data;
}

export async function stopMotor(): Promise<CommandResponse> {
  const response = await api.post('/twin/stop');
  return response.data;
}

export async function resetMotor(): Promise<CommandResponse> {
  const response = await api.post('/twin/reset');
  return response.data;
}

export async function emergencyStop(): Promise<CommandResponse> {
  const response = await api.post('/twin/emergency-stop');
  return response.data;
}

export async function setTargetSpeed(value: number): Promise<CommandResponse> {
  const response = await api.post('/twin/target-speed', { value });
  return response.data;
}

export async function setLoad(value: number): Promise<CommandResponse> {
  const response = await api.post('/twin/load', { value });
  return response.data;
}

export async function setVoltage(value: number): Promise<CommandResponse> {
  const response = await api.post('/twin/voltage', { value });
  return response.data;
}

export async function setOperatingMode(mode: string): Promise<CommandResponse> {
  const response = await api.post('/twin/operating-mode', { value: mode });
  return response.data;
}

export async function injectFault(fault: string, intensity: number = 1.0): Promise<CommandResponse> {
  const response = await api.post('/twin/inject-fault', { fault, value: intensity });
  return response.data;
}

export async function clearFault(): Promise<CommandResponse> {
  const response = await api.post('/twin/clear-fault');
  return response.data;
}

export async function getHistory(hours: number = 1, limit: number = 1000): Promise<HistoricalDataPoint[]> {
  const response = await api.get('/twin/history', { params: { hours, limit } });
  return response.data;
}

export async function getStatistics(hours: number = 1): Promise<StatisticsResponse> {
  const response = await api.get('/twin/statistics', { params: { hours } });
  return response.data;
}