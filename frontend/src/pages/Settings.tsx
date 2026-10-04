import React, { useState } from 'react';
import { getConfig } from '../services/api';
import type { MotorConfig } from '../types/twin';

export const Settings: React.FC = () => {
  const [config, setConfig] = useState<MotorConfig | null>(null);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    const fetchConfig = async () => {
      try {
        const cfg = await getConfig();
        setConfig(cfg);
      } catch (e) {
        console.error('Failed to fetch config:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchConfig();
  }, []);

  if (loading) return <div className="settings-page">Loading...</div>;
  if (!config) return <div className="settings-page">Failed to load configuration</div>;

  return (
    <div className="settings-page">
      <header className="page-header">
        <h1>SETTINGS</h1>
      </header>

      <div className="settings-grid">
        <section className="settings-section">
          <h3>Motor Configuration</h3>
          <table className="config-table">
            <tbody>
              <tr><td>Motor ID</td><td>{config.motor_id}</td></tr>
              <tr><td>Max Speed</td><td>{config.max_speed} RPM</td></tr>
              <tr><td>Max Temperature</td><td>{config.max_temperature} °C</td></tr>
              <tr><td>Max Current</td><td>{config.max_current} A</td></tr>
              <tr><td>Max Vibration</td><td>{config.max_vibration} mm/s</td></tr>
              <tr><td>Max Load</td><td>{config.max_load} %</td></tr>
              <tr><td>Max Voltage</td><td>{config.max_voltage} V</td></tr>
              <tr><td>Rated Power</td><td>{config.rated_power} kW</td></tr>
              <tr><td>Rated Torque</td><td>{config.rated_torque} Nm</td></tr>
              <tr><td>Rated Speed</td><td>{config.rated_speed} RPM</td></tr>
              <tr><td>Rated Current</td><td>{config.rated_current} A</td></tr>
              <tr><td>Rated Voltage</td><td>{config.rated_voltage} V</td></tr>
              <tr><td>Inertia</td><td>{config.inertia}</td></tr>
              <tr><td>Thermal Resistance</td><td>{config.thermal_resistance}</td></tr>
              <tr><td>Thermal Capacitance</td><td>{config.thermal_capacitance}</td></tr>
              <tr><td>Cooling Coefficient</td><td>{config.cooling_coefficient}</td></tr>
              <tr><td>Friction Coefficient</td><td>{config.friction_coefficient}</td></tr>
              <tr><td>Base Efficiency</td><td>{(config.efficiency_base * 100).toFixed(1)}%</td></tr>
            </tbody>
          </table>
        </section>

        <section className="settings-section">
          <h3>Simulation Parameters</h3>
          <table className="config-table">
            <tbody>
              <tr><td>Simulation Frequency</td><td>10 Hz</td></tr>
              <tr><td>WebSocket Update Rate</td><td>5 Hz</td></tr>
              <tr><td>Live History Points</td><td>1000</td></tr>
              <tr><td>Database Retention</td><td>30 days</td></tr>
            </tbody>
          </table>
        </section>

        <section className="settings-section">
          <h3>Anomaly Detection</h3>
          <table className="config-table">
            <tbody>
              <tr><td>Rule-based Detection</td><td>Enabled</td></tr>
              <tr><td>ML Detection</td><td>Enabled (Isolation Forest)</td></tr>
              <tr><td>Temperature Warning</td><td>{'>'} 90°C</td></tr>
              <tr><td>Temperature Critical</td><td>{'>'} 110°C</td></tr>
              <tr><td>Current Warning</td><td>{'>'} 40 A</td></tr>
              <tr><td>Current Critical</td><td>{'>'} 50 A</td></tr>
              <tr><td>Speed Warning</td><td>{'>'} 4500 RPM</td></tr>
              <tr><td>Speed Critical</td><td>{'>'} 5000 RPM</td></tr>
              <tr><td>Vibration Warning</td><td>{'>'} 5 mm/s</td></tr>
              <tr><td>Vibration Critical</td><td>{'>'} 8 mm/s</td></tr>
              <tr><td>Load Warning</td><td>{'>'} 90%</td></tr>
              <tr><td>Voltage Warning</td><td>{'<' } 300 V</td></tr>
              <tr><td>Efficiency Warning</td><td>{'<' } 70%</td></tr>
              <tr><td>Health Degraded</td><td>{'<' } 50%</td></tr>
            </tbody>
          </table>
        </section>

        <section className="settings-section">
          <h3>Prediction Settings</h3>
          <table className="config-table">
            <tbody>
              <tr><td>Prediction Enabled</td><td>Yes</td></tr>
              <tr><td>Horizon</td><td>60 seconds</td></tr>
              <tr><td>Update Interval</td><td>10 seconds</td></tr>
              <tr><td>Temperature Model</td><td>Linear Regression</td></tr>
              <tr><td>Vibration Model</td><td>Linear Regression</td></tr>
              <tr><td>Speed Model</td><td>Linear Regression</td></tr>
              <tr><td>Health Model</td><td>Linear Regression</td></tr>
            </tbody>
          </table>
        </section>

        <section className="settings-section">
          <h3>System Information</h3>
          <table className="config-table">
            <tbody>
              <tr><td>Version</td><td>1.0.0</td></tr>
              <tr><td>Build Date</td><td>{new Date().toLocaleDateString()}</td></tr>
              <tr><td>Tech Stack</td><td>React + TypeScript + FastAPI + WebSocket</td></tr>
              <tr><td>Database</td><td>SQLite (dev) / PostgreSQL (prod)</td></tr>
              <tr><td>ML Library</td><td>scikit-learn</td></tr>
              <tr><td>Charting</td><td>Recharts</td></tr>
              <tr><td>State Management</td><td>Zustand</td></tr>
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
};