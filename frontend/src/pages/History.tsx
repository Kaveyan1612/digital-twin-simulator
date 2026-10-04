import React, { useEffect, useState } from 'react';
import { useTwinStore } from '../store/twinStore';
import { getHistory } from '../services/api';
import { formatNumber, formatDateTime } from '../utils/formatting';
import { RealTimeChart, MultiLineChart } from '../components/Charts';

export const History: React.FC = () => {
  const [timeRange, setTimeRange] = useState(1);
  const [loading, setLoading] = useState(false);
  const historicalData = useTwinStore(s => s.historicalData);

  const timeRanges = [
    { value: 1, label: 'Last Hour' },
    { value: 6, label: 'Last 6 Hours' },
    { value: 24, label: 'Last 24 Hours' },
    { value: 168, label: 'Last Week' },
  ];

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const history = await getHistory(timeRange, 10000);
      useTwinStore.getState().setHistoricalData(history);
    } catch (e) {
      console.error('Failed to fetch history:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [timeRange]);

  const columns = [
    { key: 'timestamp', label: 'Time', render: (v: number) => formatDateTime(v) },
    { key: 'speed', label: 'Speed (RPM)', render: (v: number) => formatNumber(v) },
    { key: 'target_speed', label: 'Target (RPM)', render: (v: number) => formatNumber(v) },
    { key: 'load', label: 'Load (%)', render: (v: number) => formatNumber(v) },
    { key: 'torque', label: 'Torque (Nm)', render: (v: number) => formatNumber(v) },
    { key: 'voltage', label: 'Voltage (V)', render: (v: number) => formatNumber(v) },
    { key: 'current', label: 'Current (A)', render: (v: number) => formatNumber(v) },
    { key: 'power', label: 'Power (kW)', render: (v: number) => formatNumber(v, 2) },
    { key: 'temperature', label: 'Temp (°C)', render: (v: number) => formatNumber(v) },
    { key: 'vibration', label: 'Vib (mm/s)', render: (v: number) => formatNumber(v, 2) },
    { key: 'efficiency', label: 'Eff (%)', render: (v: number) => formatNumber(v) },
    { key: 'health_score', label: 'Health (%)', render: (v: number) => formatNumber(v) },
  ];

  return (
    <div className="history-page">
      <header className="page-header">
        <h1>HISTORICAL DATA</h1>
        <div className="time-range-selector">
          {timeRanges.map(({ value, label }) => (
            <button
              key={value}
              className={`btn ${timeRange === value ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange(value)}
              disabled={loading}
            >
              {label}
            </button>
          ))}
          {loading && <span className="loading">Loading...</span>}
        </div>
      </header>

      <div className="charts-section">
        <div className="chart-row">
          <div className="chart-card">
            <h3>Speed & Target Speed</h3>
            <MultiLineChart
              data={historicalData}
              lines={[
                { dataKey: 'speed', name: 'Speed', unit: 'RPM', color: '#2196F3' },
                { dataKey: 'target_speed', name: 'Target', unit: 'RPM', color: '#FF8800' },
              ]}
              height={350}
            />
          </div>
          
          <div className="chart-card">
            <h3>Temperature</h3>
            <RealTimeChart
              data={historicalData}
              dataKey="temperature"
              name="Temperature"
              unit="°C"
              color="#FF4444"
              height={350}
              yDomain={[20, 130]}
            />
          </div>
        </div>

        <div className="chart-row">
          <div className="chart-card">
            <h3>Current & Power</h3>
            <MultiLineChart
              data={historicalData}
              lines={[
                { dataKey: 'current', name: 'Current', unit: 'A', color: '#FF4444' },
                { dataKey: 'power', name: 'Power', unit: 'kW', color: '#FF8800' },
              ]}
              height={350}
            />
          </div>

          <div className="chart-card">
            <h3>Vibration & Health</h3>
            <MultiLineChart
              data={historicalData}
              lines={[
                { dataKey: 'vibration', name: 'Vibration', unit: 'mm/s', color: '#FF8800' },
                { dataKey: 'health_score', name: 'Health', unit: '%', color: '#00C851' },
              ]}
              height={350}
            />
          </div>
        </div>

        <div className="chart-row">
          <div className="chart-card">
            <h3>Efficiency & Load</h3>
            <MultiLineChart
              data={historicalData}
              lines={[
                { dataKey: 'efficiency', name: 'Efficiency', unit: '%', color: '#4CAF50' },
                { dataKey: 'load', name: 'Load', unit: '%', color: '#9C27B0' },
              ]}
              height={350}
            />
          </div>

          <div className="chart-card">
            <h3>Torque & Load</h3>
            <MultiLineChart
              data={historicalData}
              lines={[
                { dataKey: 'torque', name: 'Torque', unit: 'Nm', color: '#2196F3' },
                { dataKey: 'load', name: 'Load', unit: '%', color: '#9C27B0' },
              ]}
              height={350}
            />
          </div>
        </div>
      </div>

      <div className="data-table-container">
        <h3>Data Table ({historicalData.length} records)</h3>
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map(col => <th key={col.key}>{col.label}</th>)}
              </tr>
            </thead>
            <tbody>
              {historicalData.slice(-100).reverse().map((row, index) => (
                <tr key={index}>
                  {columns.map(col => (
                    <td key={col.key}>
                      {col.render((row as any)[col.key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};