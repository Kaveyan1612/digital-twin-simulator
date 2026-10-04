export function formatNumber(value: number, decimals: number = 1): string {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  return value.toFixed(decimals);
}

export function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatDateTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    RUNNING: '#00C851',
    STARTING: '#FF8800',
    STOPPED: '#9E9E9E',
    STOPPING: '#FF8800',
    EMERGENCY_STOP: '#FF4444',
    FAULT: '#FF4444',
    MAINTENANCE: '#2196F3',
  };
  return colors[status] || '#9E9E9E';
}

export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    INFO: '#2196F3',
    LOW: '#8BC34A',
    MEDIUM: '#FF8800',
    HIGH: '#FF4444',
    CRITICAL: '#8B0000',
  };
  return colors[severity] || '#9E9E9E';
}

export function getHealthColor(score: number): string {
  if (score >= 90) return '#00C851';
  if (score >= 75) return '#8BC34A';
  if (score >= 50) return '#FF8800';
  if (score >= 25) return '#FF4444';
  return '#8B0000';
}

export function getHealthLabel(score: number): string {
  if (score >= 90) return 'HEALTHY';
  if (score >= 75) return 'GOOD';
  if (score >= 50) return 'WARNING';
  if (score >= 25) return 'CRITICAL';
  return 'FAILURE';
}

export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export function calculateTrend(values: number[]): 'up' | 'down' | 'stable' {
  if (values.length < 2) return 'stable';
  const recent = values.slice(-10);
  const first = recent[0];
  const last = recent[recent.length - 1];
  const diff = last - first;
  const threshold = Math.abs(first) * 0.02;
  
  if (diff > threshold) return 'up';
  if (diff < -threshold) return 'down';
  return 'stable';
}