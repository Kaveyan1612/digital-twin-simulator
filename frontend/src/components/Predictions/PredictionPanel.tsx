import React from 'react';
import { useTwinStore } from '../../store/twinStore';
import { PredictionChart } from '../Charts';
import { formatNumber } from '../../utils/formatting';
import { getSeverityColor } from '../../utils/formatting';

export const PredictionPanel: React.FC = () => {
  const predictions = useTwinStore(s => s.predictions);
  const state = useTwinStore(s => s.currentState);

  const predictionTypes = [
    { key: 'temperature', name: 'Temperature', unit: '°C', color: '#FF4444', threshold: 90 },
    { key: 'vibration', name: 'Vibration', unit: 'mm/s', color: '#FF8800', threshold: 8 },
    { key: 'speed', name: 'Speed', unit: 'RPM', color: '#2196F3', threshold: null },
    { key: 'health_score', name: 'Health', unit: '%', color: '#00C851', threshold: 30 },
  ];

  if (!state) return <div className="prediction-panel">No data available</div>;

  return (
    <div className="prediction-panel">
      <h3>Predictive Analysis</h3>
      
      <div className="prediction-grid">
        {predictionTypes.map(({ key, name, unit, color, threshold }) => {
          const predData = predictions[key];
          const currentValue = key === 'temperature' ? state.temperature :
                              key === 'vibration' ? state.vibration :
                              key === 'speed' ? state.speed : state.health_score;
          
          const predictions_array = predData?.predictions || [];
          
          return (
            <div key={key} className="prediction-card">
              <div className="prediction-header">
                <span className="prediction-name">{name}</span>
                <span className="prediction-current" style={{ color }}>
                  {formatNumber(currentValue)} {unit}
                </span>
              </div>
              <PredictionChart
                predictions={predictions_array}
                currentValue={currentValue}
                name={name}
                unit={unit}
                color={color}
                warningThreshold={threshold || undefined}
                height={180}
              />
              {threshold && predictions_array.some((p: any) => p.value > threshold) && (
                <div className="predictive-warning" style={{ borderColor: getSeverityColor('HIGH') }}>
                  ⚠️ PREDICTIVE WARNING: {name} predicted to exceed {threshold}{unit}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};