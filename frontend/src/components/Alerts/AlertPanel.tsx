import React from 'react';
import { formatTimestamp } from '../../utils/formatting';
import { getSeverityColor } from '../../utils/formatting';
import type { AlertInfo, AnomalyResult } from '../../types/twin';

interface AlertPanelProps {
  alerts: AlertInfo[];
  anomalies: AnomalyResult[];
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ alerts, anomalies }) => {
  const allAlerts = [...alerts, ...anomalies.map(a => ({
    id: Date.now(),
    timestamp: a.timestamp,
    alert_type: a.anomaly_type,
    severity: a.severity,
    title: a.anomaly_type,
    message: a.description,
    parameter: a.parameter,
    current_value: a.value,
    threshold_value: a.threshold,
    acknowledged: false,
  }))].sort((a, b) => b.timestamp - a.timestamp);

  if (allAlerts.length === 0) {
    return (
      <div className="alert-panel">
        <h3>Alerts & Anomalies</h3>
        <div className="no-alerts">No active alerts</div>
      </div>
    );
  }

  return (
    <div className="alert-panel">
      <h3>Alerts & Anomalies ({allAlerts.length})</h3>
      <div className="alert-list">
        {allAlerts.map((alert) => (
          <div 
            key={alert.id || alert.timestamp}
            className="alert-item"
            style={{ borderLeftColor: getSeverityColor(alert.severity) }}
          >
            <div className="alert-header">
              <span className="alert-title">{alert.title}</span>
              <span 
                className="alert-severity"
                style={{ backgroundColor: getSeverityColor(alert.severity) }}
              >
                {alert.severity}
              </span>
            </div>
            <div className="alert-message">{alert.message}</div>
            <div className="alert-details">
              {alert.parameter && (
                <span>Parameter: {alert.parameter}</span>
              )}
              {alert.current_value !== null && alert.current_value !== undefined && (
                <span>Value: {alert.current_value.toFixed(2)}</span>
              )}
              {alert.threshold_value !== null && alert.threshold_value !== undefined && (
                <span>Threshold: {alert.threshold_value.toFixed(2)}</span>
              )}
              <span className="alert-time">{formatTimestamp(alert.timestamp)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};