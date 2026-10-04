import React from 'react';
import { formatNumber, getStatusColor, getHealthColor, getHealthLabel } from '../../utils/formatting';
import type { MotorStatus } from '../../types/twin';

interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  status?: MotorStatus;
  healthScore?: number;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
  decimals?: number;
  icon?: React.ReactNode;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit = '',
  status,
  healthScore,
  trend,
  color,
  decimals = 1,
  icon,
  className = '',
}) => {
  const displayValue = typeof value === 'number' ? formatNumber(value, decimals) : value;
  const cardColor = color || (status ? getStatusColor(status) : healthScore !== undefined ? getHealthColor(healthScore) : '#2196F3');
  
  const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
  const trendColor = trend === 'up' ? '#FF4444' : trend === 'down' ? '#00C851' : '#9E9E9E';
  
  const healthLabel = healthScore !== undefined ? getHealthLabel(healthScore) : '';

  return (
    <div className={`metric-card ${className}`} style={{ borderLeftColor: cardColor }}>
      <div className="metric-header">
        <span className="metric-title">{title}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <div className="metric-value-container">
        <span className="metric-value" style={{ color: cardColor }}>
          {displayValue}
          {unit && <span className="metric-unit">{unit}</span>}
        </span>
        {trend !== undefined && (
          <span className="metric-trend" style={{ color: trendColor }}>
            {trendIcon}
          </span>
        )}
      </div>
      {healthLabel && (
        <div className="metric-health" style={{ color: cardColor }}>
          {healthLabel}
        </div>
      )}
      {status && (
        <div className="metric-status" style={{ color: cardColor }}>
          {status}
        </div>
      )}
    </div>
  );
};