import React from 'react';
import { getSeverityColor, getStatusColor } from '../../utils/formatting';

interface StatusBadgeProps {
  label: string;
  severity?: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status?: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  label,
  severity,
  status,
  className = '',
}) => {
  const color = severity ? getSeverityColor(severity) : status ? getStatusColor(status) : '#2196F3';

  return (
    <span 
      className={`status-badge ${className}`}
      style={{ backgroundColor: `${color}20`, color, borderColor: color }}
    >
      {label}
    </span>
  );
};