export type OperatingMode = 'NORMAL' | 'HIGH_LOAD' | 'COOLING' | 'MAINTENANCE' | 'FAULT_TEST';
export type MotorStatus = 'STOPPED' | 'STARTING' | 'RUNNING' | 'STOPPING' | 'EMERGENCY_STOP' | 'FAULT' | 'MAINTENANCE';
export type AnomalySeverity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type FaultType = 'overtemperature' | 'overcurrent' | 'high_vibration' | 'overspeed' | 'undervoltage' | 'overload' | 'sensor_anomaly' | 'combined';

export interface MotorState {
  timestamp: number;
  motor_id: string;
  running: boolean;
  operating_mode: OperatingMode;
  target_speed: number;
  speed: number;
  load: number;
  torque: number;
  voltage: number;
  current: number;
  power: number;
  temperature: number;
  vibration: number;
  efficiency: number;
  health_score: number;
  status: MotorStatus;
  anomaly_detected: boolean;
  anomaly_type: string | null;
  anomaly_severity: AnomalySeverity | null;
}

export interface MotorConfig {
  motor_id: string;
  max_speed: number;
  max_temperature: number;
  max_current: number;
  max_vibration: number;
  max_load: number;
  max_voltage: number;
  rated_power: number;
  rated_torque: number;
  rated_speed: number;
  rated_current: number;
  rated_voltage: number;
  inertia: number;
  thermal_resistance: number;
  thermal_capacitance: number;
  cooling_coefficient: number;
  friction_coefficient: number;
  efficiency_base: number;
}

export interface AnomalyResult {
  anomaly_detected: boolean;
  severity: AnomalySeverity;
  anomaly_type: string | null;
  confidence: number;
  timestamp: number;
  description: string;
  parameter: string | null;
  value: number | null;
  threshold: number | null;
}

export interface PredictionResult {
  prediction_type: string;
  horizon_seconds: number;
  predicted_value: number;
  confidence: number;
  timestamp: number;
  model_version: string;
}

export interface HealthScore {
  score: number;
  temperature_factor: number;
  vibration_factor: number;
  current_factor: number;
  speed_deviation_factor: number;
  load_factor: number;
  efficiency_factor: number;
  fault_factor: number;
}

export interface AlertInfo {
  id?: number;
  timestamp: number;
  alert_type: string;
  severity: AnomalySeverity;
  title: string;
  message: string;
  parameter: string | null;
  current_value: number | null;
  threshold_value: number | null;
  acknowledged: boolean;
}

export interface CommandRequest {
  type: string;
  value?: number;
  fault?: FaultType;
}

export interface CommandResponse {
  success: boolean;
  message: string;
  command_id?: number;
}

export interface HistoricalDataPoint {
  timestamp: number;
  speed: number;
  target_speed: number;
  load: number;
  torque: number;
  voltage: number;
  current: number;
  power: number;
  temperature: number;
  vibration: number;
  efficiency: number;
  health_score: number;
}

export interface StatisticsResponse {
  avg_speed: number;
  max_speed: number;
  avg_temperature: number;
  max_temperature: number;
  avg_load: number;
  avg_current: number;
  avg_power: number;
  avg_efficiency: number;
  avg_vibration: number;
  min_health_score: number;
  data_points: number;
  anomaly_count: number;
  critical_fault_count: number;
  uptime_seconds: number;
}

export interface HealthResponse {
  status: string;
  simulation_running: boolean;
  database: string;
  websocket_clients: number;
  uptime_seconds: number;
}

export interface WebSocketMessage {
  type: string;
  timestamp: number;
  data?: any;
}

export interface PredictionForecast {
  prediction_type: string;
  current_value: number;
  predictions: Array<{ time: number; value: number; ml_value?: number }>;
  warning?: string;
  warning_threshold?: number;
}

export interface WebSocketIncomingMessage {
  type: string;
  value?: number;
  fault?: string;
}