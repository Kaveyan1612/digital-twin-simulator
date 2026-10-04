import React, { useEffect } from 'react';
import { useTwinStore } from '../store/twinStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { useTwinControls } from '../hooks/useTwinState';
import {
  MetricCard,
  ConnectionStatus,
  StatusBadge,
  EventLog,
} from '../components/Common';
import { MotorVisualization } from '../components/Motor';
import {
  RealTimeChart,
  MultiLineChart,
} from '../components/Charts';
import { ControlPanel, FaultInjectionPanel } from '../components/Controls';
import { AlertPanel } from '../components/Alerts';
import { PredictionPanel } from '../components/Predictions';

export const Dashboard: React.FC = () => {
  const state = useTwinStore(s => s.currentState);
  const connectionStatus = useTwinStore(s => s.connectionStatus);
  const alerts = useTwinStore(s => s.alerts);
  const anomalies = useTwinStore(s => s.anomalies);
  const lastMessageTime = useTwinStore(s => s.currentState?.timestamp);

  useTwinControls();

  useWebSocket();

  useEffect(() => {
    if (state) {
      console.log('State updated:', state.status, state.speed, state.temperature);
    }
  }, [state]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>DIGITAL TWIN SIMULATOR</h1>
          <span className="motor-id">{state?.motor_id || 'MOTOR-001'}</span>
        </div>
        <div className="header-right">
          <ConnectionStatus status={connectionStatus} lastMessageTime={lastMessageTime} />
        </div>
      </header>

      <div className="dashboard-grid">
        <section className="status-section">
          <div className="metric-row">
            <MetricCard
              title="STATUS"
              value={state?.status || 'UNKNOWN'}
              status={state?.status as any}
            />
            <MetricCard
              title="HEALTH"
              value={state?.health_score || 0}
              unit="%"
              healthScore={state?.health_score}
            />
            <MetricCard
              title="SPEED"
              value={state?.speed || 0}
              unit="RPM"
              color="#2196F3"
            />
            <MetricCard
              title="TEMPERATURE"
              value={state?.temperature || 0}
              unit="°C"
              color="#FF4444"
            />
            <MetricCard
              title="VIBRATION"
              value={state?.vibration || 0}
              unit="mm/s"
              color="#FF8800"
              decimals={2}
            />
          </div>

          <div className="metric-row">
            <MetricCard
              title="CURRENT"
              value={state?.current || 0}
              unit="A"
              color="#FF4444"
            />
            <MetricCard
              title="POWER"
              value={state?.power || 0}
              unit="kW"
              color="#FF8800"
            />
            <MetricCard
              title="TORQUE"
              value={state?.torque || 0}
              unit="Nm"
              color="#2196F3"
            />
            <MetricCard
              title="LOAD"
              value={state?.load || 0}
              unit="%"
              color="#9C27B0"
            />
            <MetricCard
              title="EFFICIENCY"
              value={state?.efficiency || 0}
              unit="%"
              color="#4CAF50"
            />
          </div>

          {state?.anomaly_detected && (
            <div className="anomaly-banner">
              <StatusBadge 
                label={`ANOMALY: ${state.anomaly_type} (${state.anomaly_severity || 'UNKNOWN'})`}
                severity={state.anomaly_severity || 'HIGH'}
              />
            </div>
          )}
        </section>

        <section className="visualization-section">
          <MotorVisualization state={state} size={280} />
        </section>
      </div>

      <div className="charts-section">
        <div className="chart-row">
          <div className="chart-card">
            <h3>Speed & Target Speed</h3>
            <MultiLineChart
              data={useTwinStore.getState().historicalData}
              lines={[
                { dataKey: 'speed', name: 'Speed', unit: 'RPM', color: '#2196F3' },
                { dataKey: 'target_speed', name: 'Target', unit: 'RPM', color: '#FF8800' },
              ]}
              height={250}
            />
          </div>
          
          <div className="chart-card">
            <h3>Temperature</h3>
            <RealTimeChart
              data={useTwinStore.getState().historicalData}
              dataKey="temperature"
              name="Temperature"
              unit="°C"
              color="#FF4444"
              height={250}
              yDomain={[20, 130]}
            />
          </div>
        </div>

        <div className="chart-row">
          <div className="chart-card">
            <h3>Current & Power</h3>
            <MultiLineChart
              data={useTwinStore.getState().historicalData}
              lines={[
                { dataKey: 'current', name: 'Current', unit: 'A', color: '#FF4444' },
                { dataKey: 'power', name: 'Power', unit: 'kW', color: '#FF8800' },
              ]}
              height={250}
            />
          </div>

          <div className="chart-card">
            <h3>Vibration</h3>
            <RealTimeChart
              data={useTwinStore.getState().historicalData}
              dataKey="vibration"
              name="Vibration"
              unit="mm/s"
              color="#FF8800"
              height={250}
              yDomain={[0, 12]}
            />
          </div>
        </div>

        <div className="chart-row">
          <div className="chart-card">
            <h3>Torque & Load</h3>
            <MultiLineChart
              data={useTwinStore.getState().historicalData}
              lines={[
                { dataKey: 'torque', name: 'Torque', unit: 'Nm', color: '#2196F3' },
                { dataKey: 'load', name: 'Load', unit: '%', color: '#9C27B0' },
              ]}
              height={250}
            />
          </div>

          <div className="chart-card">
            <h3>Efficiency & Health</h3>
            <MultiLineChart
              data={useTwinStore.getState().historicalData}
              lines={[
                { dataKey: 'efficiency', name: 'Efficiency', unit: '%', color: '#4CAF50' },
                { dataKey: 'health_score', name: 'Health', unit: '%', color: '#00C851' },
              ]}
              height={250}
            />
          </div>
        </div>
      </div>

      <div className="bottom-section">
        <div className="bottom-left">
          <AlertPanel alerts={alerts} anomalies={anomalies} />
        </div>
        <div className="bottom-right">
          <PredictionPanel />
        </div>
      </div>

      <div className="controls-section">
        <ControlPanel />
        <FaultInjectionPanel />
      </div>

      <div className="event-section">
        <EventLog />
      </div>
    </div>
  );
};