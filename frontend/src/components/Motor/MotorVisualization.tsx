import React from 'react';
import { formatNumber } from '../../utils/formatting';
import type { MotorState, MotorStatus } from '../../types/twin';

interface MotorVisualizationProps {
  state: MotorState | null;
  size?: number;
}

export const MotorVisualization: React.FC<MotorVisualizationProps> = ({
  state,
  size = 200,
}) => {
  if (!state) return <div className="motor-visualization-placeholder">No data</div>;

  const temperatureRatio = Math.min(state.temperature / 120, 1);
  const vibrationIntensity = Math.min(state.vibration / 10, 1);
  
  const shaftRotation = state.running ? `${(Date.now() / 50) % 360}deg` : '0deg';
  const tempColor = `hsl(${120 - temperatureRatio * 120}, 100%, 50%)`;
  const vibColor = `hsl(${120 - vibrationIntensity * 120}, 100%, 50%)`;

  return (
    <div className="motor-visualization" style={{ width: size, height: size }}>
      <div className="motor-body" style={{ backgroundColor: tempColor }}>
        <div 
          className="motor-shaft"
          style={{ transform: `rotate(${shaftRotation})` }}
        >
          <div className="shaft-end" />
        </div>
        <div className="motor-label">
          {state.motor_id}
        </div>
        <div className="motor-status" style={{ backgroundColor: getStatusColor(state.status) }}>
          {state.status}
        </div>
      </div>
      
      <div className="motor-indicators">
        <div className="indicator">
          <div 
            className="indicator-bar temperature"
            style={{ height: `${temperatureRatio * 100}%`, backgroundColor: tempColor }}
          />
          <span className="indicator-label">TEMP</span>
          <span className="indicator-value">{formatNumber(state.temperature)}°C</span>
        </div>
        
        <div className="indicator">
          <div 
            className="indicator-bar vibration"
            style={{ height: `${vibrationIntensity * 100}%`, backgroundColor: vibColor }}
          />
          <span className="indicator-label">VIB</span>
          <span className="indicator-value">{formatNumber(state.vibration, 2)} mm/s</span>
        </div>
        
        <div className="indicator">
          <div className="speed-display">
            <span className="speed-value">{formatNumber(state.speed)}</span>
            <span className="speed-unit">RPM</span>
          </div>
          <span className="indicator-label">SPEED</span>
        </div>
        
        <div className="indicator">
          <div className="health-display">
            <div 
              className="health-ring"
              style={{ 
                background: `conic-gradient(${getStatusColor(state.status)} ${state.health_score}%, transparent ${state.health_score}%)` 
              }}
            >
              <span className="health-value">{formatNumber(state.health_score)}%</span>
            </div>
          </div>
          <span className="indicator-label">HEALTH</span>
        </div>
      </div>
    </div>
  );
};

function getStatusColor(status: MotorStatus): string {
  const colors: Record<string, string> = {
    RUNNING: '#00C851',
    STARTING: '#FF8800',
    STOPPED: '#9E9E9E',
    STOPPING: '#FF8800',
    EMERGENCY_STOP: '#FF4444',
    FAULT: '#FF4444',
    MAINTENANCE: '#2196F3',
  };
  return colors[status] || '#9E9E9E';
}