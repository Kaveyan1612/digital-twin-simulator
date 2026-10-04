import { act, renderHook } from '@testing-library/react';
import { useTwinStore } from '../store/twinStore';
import type { MotorState, AlertInfo, AnomalyResult } from '../types/twin';

describe('useTwinStore', () => {
  const mockState: MotorState = {
    timestamp: Date.now(),
    motor_id: 'MOTOR-001',
    running: true,
    operating_mode: 'NORMAL',
    target_speed: 3000,
    speed: 2950,
    load: 50,
    torque: 30,
    voltage: 415,
    current: 15,
    power: 5.5,
    temperature: 65,
    vibration: 1.5,
    efficiency: 92,
    health_score: 94,
    status: 'RUNNING',
    anomaly_detected: false,
    anomaly_type: null,
    anomaly_severity: 'INFO',
  };

  const mockAlert: AlertInfo = {
    id: 1,
    timestamp: Date.now(),
    alert_type: 'OVERTEMPERATURE',
    severity: 'HIGH',
    title: 'High Temperature',
    message: 'Temperature exceeds threshold',
    parameter: 'temperature',
    current_value: 95,
    threshold_value: 90,
    acknowledged: false,
  };

  const mockAnomaly: AnomalyResult = {
    anomaly_detected: true,
    severity: 'HIGH',
    anomaly_type: 'OVERTEMPERATURE_WARNING',
    confidence: 1.0,
    timestamp: Date.now(),
    description: 'Temperature exceeds warning threshold',
    parameter: 'temperature',
    value: 95,
    threshold: 90,
  };

  beforeEach(() => {
    act(() => {
      useTwinStore.getState().setCurrentState(null);
      useTwinStore.getState().clearAlerts();
      useTwinStore.getState().clearAnomalies();
      useTwinStore.getState().setConnectionStatus('disconnected');
      useTwinStore.getState().clearEventLog();
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
    expect(result.current.alerts[0]).toEqual(mockAlert);
  });

  test('does not add duplicate alerts', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addAlert(mockAlert);
      result.current.addAlert(mockAlert);
    });
    
    expect(result.current.alerts).toHaveLength(1);
  });

  test('clears alerts', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addAlert(mockAlert);
      result.current.clearAlerts();
    });
    
    expect(result.current.alerts).toHaveLength(0);
  });

  test('acknowledges alert', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addAlert(mockAlert);
      result.current.acknowledgeAlert(1);
    });
    
    expect(result.current.alerts[0].acknowledged).toBe(true);
  });

  test('adds and retrieves anomalies', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addAnomaly(mockAnomaly);
    });
    
    expect(result.current.anomalies).toHaveLength(1);
    expect(result.current.anomalies[0]).toEqual(mockAnomaly);
  });

  test('clears anomalies', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addAnomaly(mockAnomaly);
      result.current.clearAnomalies();
    });
    
    expect(result.current.anomalies).toHaveLength(0);
  });

  test('sets predictions', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.setPredictions('temperature', [mockAnomaly as any]);
    });
    
    expect(result.current.predictions.temperature).toHaveLength(1);
  });

  test('sets historical data', () => {
    const { result } = renderHook(() => useTwinStore());
    const historyData = [mockState];
    
    act(() => {
      result.current.setHistoricalData(historyData as any);
    });
    
    expect(result.current.historicalData).toEqual(historyData);
  });

  test('sets statistics', () => {
    const { result } = renderHook(() => useTwinStore());
    const stats = { avg_speed: 3000, max_temperature: 80 };
    
    act(() => {
      result.current.setStatistics(stats as any);
    });
    
    expect(result.current.statistics).toEqual(stats);
  });

  test('sets connection status', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.setConnectionStatus('connected');
    });
    
    expect(result.current.connectionStatus).toBe('connected');
  });

  test('adds events to log', () => {
    const { result } = renderHook(() => useTwinStore());
    const event = { timestamp: Date.now(), message: 'Test event', type: 'info' };
    
    act(() => {
      result.current.addEvent(event);
    });
    
    expect(result.current.eventLog).toHaveLength(1);
    expect(result.current.eventLog[0]).toEqual(event);
  });

  test('clears event log', () => {
    const { result } = renderHook(() => useTwinStore());
    
    act(() => {
      result.current.addEvent({ timestamp: Date.now(), message: 'Test', type: 'info' });
      result.current.clearEventLog();
    });
    
    expect(result.current.eventLog).toHaveLength(0);
  });

  test('limits history size', () => {
    const { result } = renderHook(() => useTwinStore());
    const largeHistory = Array(1500).fill(mockState);
    
    act(() => {
      result.current.setHistoricalData(largeHistory as any);
    });
    
    expect(result.current.historicalData.length).toBeLessThanOrEqual(1000);
  });

  test('limits alerts size', () => {
    const { result } = renderHook(() => useTwinStore());
    const alerts = Array(150).fill(null).map((_, i) => ({ ...mockAlert, id: i }));
    
    act(() => {
      alerts.forEach(alert => result.current.addAlert(alert));
    });
    
    expect(result.current.alerts.length).toBeLessThanOrEqual(100);
  });

  test('limits anomalies size', () => {
    const { result } = renderHook(() => useTwinStore());
    const anomalies = Array(150).fill(null).map((_, i) => ({ ...mockAnomaly, timestamp: Date.now() + i }));
    
    act(() => {
      anomalies.forEach(anomaly => result.current.addAnomaly(anomaly));
    });
    
    expect(result.current.anomalies.length).toBeLessThanOrEqual(100);
  });
});