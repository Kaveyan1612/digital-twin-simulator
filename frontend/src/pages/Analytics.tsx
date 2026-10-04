import React, { useEffect, useState } from 'react';
import { useTwinStore } from '../store/twinStore';
import { getHistory, getStatistics } from '../services/api';
import { formatDuration } from '../utils/formatting';
import { MetricCard } from '../components/Common';
import { RealTimeChart, MultiLineChart, HealthGauge } from '../components/Charts';

export const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState(1);
  const [statistics, setStatistics] = useState<any>(null);
  const historicalData = useTwinStore(s => s.historicalData);

  const timeRanges = [
    { value: 1, label: 'Last Hour' },
    { value: 6, label: 'Last 6 Hours' },
    { value: 24, label: 'Last 24 Hours' },
    { value: 168, label: 'Last Week' },
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [history, stats] = await Promise.all([
        getHistory(timeRange, 5000),
        getStatistics(timeRange),
      ]);
      useTwinStore.getState().setHistoricalData(history);
      setStatistics(stats);
    } catch (e) {
      console.error('Failed to fetch analytics:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [timeRange]);

  if (!statistics) {
    return <div className="analytics-page">Loading...</div>;
  }

  return (
    <div className="analytics-page">
      <header className="page-header">
        <h1>ANALYTICS</h1>
        <div className="time-range-selector">
          {timeRanges.map(({ value, label }) => (
            <button
              key={value}
              className={`btn ${timeRange === value ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTimeRange(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </header>

      <div className="stats-grid">
        <MetricCard title="Avg Speed" value={statistics.avg_speed} unit="RPM" color="#2196F3" />
        <MetricCard title="Max Speed" value={statistics.max_speed} unit="RPM" color="#2196F3" />
        <MetricCard title="Avg Temperature" value={statistics.avg_temperature} unit="°C" color="#FF4444" />
        <MetricCard title="Max Temperature" value={statistics.max_temperature} unit="°C" color="#FF4444" />
        <MetricCard title="Avg Load" value={statistics.avg_load} unit="%" color="#9C27B0" />
        <MetricCard title="Avg Current" value={statistics.avg_current} unit="A" color="#FF4444" />
        <MetricCard title="Avg Power" value={statistics.avg_power} unit="kW" color="#FF8800" />
        <MetricCard title="Avg Efficiency" value={statistics.avg_efficiency} unit="%" color="#4CAF50" />
        <MetricCard title="Avg Vibration" value={statistics.avg_vibration} unit="mm/s" color="#FF8800" decimals={2} />
        <MetricCard title="Min Health" value={statistics.min_health_score} unit="%" color="#00C851" />
        <MetricCard title="Data Points" value={statistics.data_points} unit="" color="#2196F3" />
        <MetricCard title="Uptime" value={formatDuration(statistics.uptime_seconds)} unit="" color="#9C27B0" />
        <MetricCard title="Anomalies" value={statistics.anomaly_count} unit="" color="#FF4444" />
        <MetricCard title="Critical Faults" value={statistics.critical_fault_count} unit="" color="#8B0000" />
      </div>

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
              height={300}
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
              height={300}
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
              height={300}
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
              height={300}
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
              height={300}
            />
          </div>

          <div className="chart-card">
            <h3>Health Score Gauge</h3>
            <HealthGauge score={statistics.min_health_score} size={200} />
          </div>
        </div>
      </div>
    </div>
  );
};