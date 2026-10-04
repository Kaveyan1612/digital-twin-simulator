import React from 'react';
import {
  RadialBarChart,
  RadialBar,
  Cell,
} from 'recharts';
import { formatNumber } from '../../utils/formatting';

interface GaugeChartProps {
  value: number;
  max?: number;
  min?: number;
  label: string;
  unit?: string;
  color?: string;
  thresholds?: Array<{ value: number; color: string }>;
  size?: number;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({
  value,
  max = 100,
  min = 0,
  label,
  unit = '',
  color = '#00C851',
  thresholds,
  size = 150,
}) => {
  const percentage = ((value - min) / (max - min)) * 100;
  const clampedPercentage = Math.max(0, Math.min(100, percentage));

  let gaugeColor = color;
  if (thresholds) {
    for (const threshold of thresholds) {
      if (value >= threshold.value) {
        gaugeColor = threshold.color;
      }
    }
  }

  return (
    <div className="gauge-chart" style={{ width: size, height: size }}>
      <RadialBarChart width={size} height={size}>
        <RadialBar
          startAngle={-90}
          endAngle={90}
          dataKey="value"
          data={[{ value: clampedPercentage, name: label }]}
          background={{ fill: '#333' }}
        >
          <Cell fill={gaugeColor} />
        </RadialBar>
      </RadialBarChart>
      <div className="gauge-label">
        <span className="gauge-value" style={{ color: gaugeColor }}>
          {formatNumber(value)}
          {unit && <span className="gauge-unit">{unit}</span>}
        </span>
        <span className="gauge-name">{label}</span>
      </div>
    </div>
  );
};

interface HealthGaugeProps {
  score: number;
  size?: number;
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({ score, size = 150 }) => {
  const getColor = (s: number) => {
    if (s >= 90) return '#00C851';
    if (s >= 75) return '#8BC34A';
    if (s >= 50) return '#FF8800';
    if (s >= 25) return '#FF4444';
    return '#8B0000';
  };

  return (
    <GaugeChart
      value={score}
      max={100}
      min={0}
      label="HEALTH"
      unit="%"
      color={getColor(score)}
      thresholds={[
        { value: 90, color: '#00C851' },
        { value: 75, color: '#8BC34A' },
        { value: 50, color: '#FF8800' },
        { value: 25, color: '#FF4444' },
        { value: 0, color: '#8B0000' },
      ]}
      size={size}
    />
  );
};