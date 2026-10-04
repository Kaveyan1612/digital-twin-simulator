import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface PredictionChartProps {
  predictions: Array<{ time: number; value: number; ml_value?: number }>;
  currentValue: number;
  name: string;
  unit: string;
  color: string;
  mlColor?: string;
  warningThreshold?: number;
  height?: number;
}

export const PredictionChart: React.FC<PredictionChartProps> = ({
  predictions,
  currentValue,
  name,
  unit,
  color,
  mlColor = '#FF8800',
  warningThreshold,
  height = 200,
}) => {
  const data = [
    { time: 'Now', value: currentValue, type: 'current' },
    ...predictions.map((p) => ({
      time: `+${Math.round(p.time)}s`,
      value: p.value,
      mlValue: p.ml_value,
      type: 'predicted',
    })),
  ];

  return (
    <div className="chart-container" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
          <XAxis
            dataKey="time"
            tick={{ fill: '#888', fontSize: 10 }}
            axisLine={{ stroke: '#333' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#888', fontSize: 10 }}
            axisLine={{ stroke: '#333' }}
            tickLine={false}
            tickFormatter={(value) => `${value}${unit}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e1e1e',
              border: '1px solid #333',
              borderRadius: '4px',
            }}
            formatter={(value: number, name: string) => [`${value.toFixed(2)} ${unit}`, name]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            name={`${name} (${unit})`}
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, strokeWidth: 2 }}
            animationDuration={300}
          />
          {predictions.some(p => p.ml_value !== undefined) && (
            <Line
              type="monotone"
              dataKey="mlValue"
              name={`${name} ML (${unit})`}
              stroke={mlColor}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              activeDot={{ r: 6, strokeWidth: 2 }}
              animationDuration={300}
            />
          )}
          {warningThreshold && (
            <Line
              type="monotone"
              dataKey="warning"
              stroke="#FF4444"
              strokeWidth={1}
              strokeDasharray="3 3"
              dot={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="prediction-legend">
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: color }} />
          Current / Predicted
        </span>
        {predictions.some(p => p.ml_value !== undefined) && (
          <span className="legend-item">
            <span className="legend-color" style={{ backgroundColor: mlColor }} />
            ML Prediction
          </span>
        )}
        {warningThreshold && (
          <span className="legend-item warning">
            <span className="legend-color" style={{ backgroundColor: '#FF4444' }} />
            Warning Threshold
          </span>
        )}
      </div>
    </div>
  );
};