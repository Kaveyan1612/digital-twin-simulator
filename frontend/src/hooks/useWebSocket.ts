import { useEffect, useCallback } from 'react';
import { websocketService } from '../services/websocket';
import { useTwinStore } from '../store/twinStore';
import type { MotorState, AnomalyResult, AlertInfo } from '../types/twin';

export function useWebSocket(url?: string) {
  const setCurrentState = useTwinStore((s) => s.setCurrentState);
  const addAlert = useTwinStore((s) => s.addAlert);
  const addAnomaly = useTwinStore((s) => s.addAnomaly);
  const setPredictions = useTwinStore((s) => s.setPredictions);
  const setConnectionStatus = useTwinStore((s) => s.setConnectionStatus);
  const addEvent = useTwinStore((s) => s.addEvent);

  const handleState = useCallback((state: MotorState) => {
    setCurrentState(state);
  }, [setCurrentState]);

  const handleAnomaly = useCallback((anomaly: AnomalyResult) => {
    addAnomaly(anomaly);
    addEvent({
      timestamp: anomaly.timestamp,
      message: `Anomaly detected: ${anomaly.anomaly_type} - ${anomaly.description}`,
      type: 'anomaly',
    });
  }, [addAnomaly, addEvent]);

  const handlePrediction = useCallback((data: { prediction_type: string; predictions: Array<{ time: number; value: number; ml_value?: number }> }) => {
    setPredictions(data.prediction_type, {
      prediction_type: data.prediction_type,
      current_value: 0,
      predictions: data.predictions,
    });
  }, [setPredictions]);

  const handleAlert = useCallback((alert: AlertInfo) => {
    addAlert(alert);
    addEvent({
      timestamp: alert.timestamp,
      message: `Alert: ${alert.title} - ${alert.message}`,
      type: 'alert',
    });
  }, [addAlert, addEvent]);

  const handleConnection = useCallback((connected: boolean) => {
    setConnectionStatus(connected ? 'connected' : 'disconnected');
    addEvent({
      timestamp: Date.now(),
      message: connected ? 'WebSocket connected' : 'WebSocket disconnected',
      type: connected ? 'info' : 'warning',
    });
  }, [setConnectionStatus, addEvent]);

  useEffect(() => {
    const unsubState = websocketService.onState(handleState);
    const unsubAnomaly = websocketService.onAnomaly(handleAnomaly);
    const unsubPrediction = websocketService.onPrediction(handlePrediction);
    const unsubAlert = websocketService.onAlert(handleAlert);
    const unsubConnection = websocketService.onConnectionChange(handleConnection);

    websocketService.connect(url);

    return () => {
      unsubState();
      unsubAnomaly();
      unsubPrediction();
      unsubAlert();
      unsubConnection();
      websocketService.disconnect();
    };
  }, [url, handleState, handleAnomaly, handlePrediction, handleAlert, handleConnection]);

  return websocketService;
}