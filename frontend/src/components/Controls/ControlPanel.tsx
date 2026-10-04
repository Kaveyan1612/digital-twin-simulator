import React from 'react';
import { useTwinStore } from '../../store/twinStore';
import { useTwinControls } from '../../hooks/useTwinState';
import type { FaultType } from '../../types/twin';
import { formatNumber } from '../../utils/formatting';

export const ControlPanel: React.FC = () => {
  const { 
    start, stop, reset, emergencyStop,
    setTargetSpeed, setLoad, setVoltage, setOperatingMode
  } = useTwinControls();
  const state = useTwinStore(s => s.currentState);

  return (
    <div className="control-panel">
      <h3>Motor Controls</h3>
      
      <div className="control-group">
        <h4>Motor State</h4>
        <div className="button-group">
          <button 
            className="btn btn-success"
            onClick={start}
            disabled={state?.running}
          >
            START
          </button>
          <button 
            className="btn btn-warning"
            onClick={stop}
            disabled={!state?.running}
          >
            STOP
          </button>
          <button 
            className="btn btn-secondary"
            onClick={reset}
          >
            RESET
          </button>
          <button 
            className="btn btn-danger"
            onClick={emergencyStop}
            disabled={!state?.running && state?.status !== 'EMERGENCY_STOP'}
          >
            EMERGENCY STOP
          </button>
        </div>
      </div>

      <div className="control-group">
        <h4>Target Speed</h4>
        <div className="slider-control">
          <input
            type="range"
            min="0"
            max="5000"
            step="100"
            value={state?.target_speed || 0}
            onChange={(e) => setTargetSpeed(Number(e.target.value))}
            disabled={!state?.running}
          />
          <span className="slider-value">{formatNumber(state?.target_speed || 0)} RPM</span>
        </div>
      </div>

      <div className="control-group">
        <h4>Load</h4>
        <div className="slider-control">
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={state?.load || 0}
            onChange={(e) => setLoad(Number(e.target.value))}
            disabled={!state?.running}
          />
          <span className="slider-value">{formatNumber(state?.load || 0)}%</span>
        </div>
      </div>

      <div className="control-group">
        <h4>Voltage</h4>
        <div className="slider-control">
          <input
            type="range"
            min="0"
            max="500"
            step="10"
            value={state?.voltage || 0}
            onChange={(e) => setVoltage(Number(e.target.value))}
            disabled={!state?.running}
          />
          <span className="slider-value">{formatNumber(state?.voltage || 0)} V</span>
        </div>
      </div>

      <div className="control-group">
        <h4>Operating Mode</h4>
        <select
          value={state?.operating_mode || 'NORMAL'}
          onChange={(e) => setOperatingMode(e.target.value)}
          disabled={!state?.running}
        >
          <option value="NORMAL">NORMAL</option>
          <option value="HIGH_LOAD">HIGH_LOAD</option>
          <option value="COOLING">COOLING</option>
          <option value="MAINTENANCE">MAINTENANCE</option>
          <option value="FAULT_TEST">FAULT_TEST</option>
        </select>
      </div>
    </div>
  );
};

const FAULT_TYPES: Array<{ value: FaultType; label: string }> = [
  { value: 'overtemperature', label: 'Overtemperature' },
  { value: 'overcurrent', label: 'Overcurrent' },
  { value: 'high_vibration', label: 'High Vibration' },
  { value: 'overspeed', label: 'Overspeed' },
  { value: 'undervoltage', label: 'Undervoltage' },
  { value: 'overload', label: 'Overload' },
  { value: 'sensor_anomaly', label: 'Sensor Anomaly' },
  { value: 'combined', label: 'Combined Fault' },
];

export const FaultInjectionPanel: React.FC = () => {
  const { injectFault, clearFault } = useTwinControls();
  const state = useTwinStore(s => s.currentState);

  return (
    <div className="control-panel fault-panel">
      <h3>Fault Injection</h3>
      <p className="fault-warning">⚠️ Use for testing anomaly detection</p>
      
      <div className="fault-grid">
        {FAULT_TYPES.map(({ value, label }) => (
          <button
            key={value}
            className="btn btn-fault"
            onClick={() => injectFault(value, 1.0)}
            disabled={!state?.running}
          >
            {label}
          </button>
        ))}
      </div>

      <button 
        className="btn btn-secondary clear-fault-btn"
        onClick={clearFault}
        disabled={!state?.anomaly_detected}
      >
        CLEAR FAULT
      </button>
    </div>
  );
};