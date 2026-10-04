import type { WebSocketMessage, WebSocketIncomingMessage, MotorState, AnomalyResult, AlertInfo } from '../types/twin';

type MessageHandler = (message: WebSocketMessage) => void;
type StateHandler = (state: MotorState) => void;
type AnomalyHandler = (anomaly: AnomalyResult) => void;
type PredictionHandler = (data: { prediction_type: string; predictions: Array<{ time: number; value: number; ml_value?: number }> }) => void;
type AlertHandler = (alert: AlertInfo) => void;
type ConnectionHandler = (connected: boolean) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private url = '';
  private messageHandlers: Set<MessageHandler> = new Set();
  private stateHandlers: Set<StateHandler> = new Set();
  private anomalyHandlers: Set<AnomalyHandler> = new Set();
  private predictionHandlers: Set<PredictionHandler> = new Set();
  private alertHandlers: Set<AlertHandler> = new Set();
  private connectionHandlers: Set<ConnectionHandler> = new Set();
  private connected = false;
  private reconnecting = false;

  connect(url: string = 'ws://localhost:8000/ws/twin') {
    this.url = url;
    this.createConnection();
  }

  private createConnection() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.connected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.notifyConnectionHandlers(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.connected = false;
        this.notifyConnectionHandlers(false);
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (e) {
      console.error('Failed to create WebSocket connection:', e);
      this.attemptReconnect();
    }
  }

  private handleMessage(message: WebSocketMessage) {
    this.messageHandlers.forEach(handler => handler(message));

    switch (message.type) {
      case 'twin_state':
        this.stateHandlers.forEach(handler => handler(message.data));
        break;
      case 'anomaly':
        this.anomalyHandlers.forEach(handler => handler(message.data));
        break;
      case 'prediction':
        this.predictionHandlers.forEach(handler => handler(message.data));
        break;
      case 'alert':
        this.alertHandlers.forEach(handler => handler(message.data));
        break;
      case 'command_ack':
        console.log('Command acknowledged:', message.data);
        break;
      case 'error':
        console.error('Server error:', message.data);
        break;
      case 'connection':
        console.log('Connection status:', message.data);
        break;
    }
  }

  private attemptReconnect() {
    if (this.reconnecting || this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    this.reconnecting = true;
    const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts), this.maxReconnectDelay);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
    
    setTimeout(() => {
      this.reconnectAttempts++;
      this.reconnecting = false;
      this.createConnection();
    }, delay);
  }

  send(message: WebSocketIncomingMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  onMessage(handler: MessageHandler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onState(handler: StateHandler) {
    this.stateHandlers.add(handler);
    return () => this.stateHandlers.delete(handler);
  }

  onAnomaly(handler: AnomalyHandler) {
    this.anomalyHandlers.add(handler);
    return () => this.anomalyHandlers.delete(handler);
  }

  onPrediction(handler: PredictionHandler) {
    this.predictionHandlers.add(handler);
    return () => this.predictionHandlers.delete(handler);
  }

  onAlert(handler: AlertHandler) {
    this.alertHandlers.add(handler);
    return () => this.alertHandlers.delete(handler);
  }

  onConnectionChange(handler: ConnectionHandler) {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  private notifyConnectionHandlers(connected: boolean) {
    this.connectionHandlers.forEach(handler => handler(connected));
  }

  sendCommand(type: string, value?: number, fault?: string) {
    this.send({ type, value, fault });
  }
}

export const websocketService = new WebSocketService();