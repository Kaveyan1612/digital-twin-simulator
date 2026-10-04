import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MetricCard } from '../components/Common/MetricCard';
import { StatusBadge } from '../components/Common/StatusBadge';
import { ConnectionStatus } from '../components/Common/ConnectionStatus';

describe('MetricCard', () => {
  test('renders title and value correctly', () => {
    render(<MetricCard title="TEMPERATURE" value={67.4} unit="°C" />);
    expect(screen.getByText('TEMPERATURE')).toBeInTheDocument();
    expect(screen.getByText('67.4')).toBeInTheDocument();
    expect(screen.getByText('°C')).toBeInTheDocument();
  });

  test('renders with status color', () => {
    render(<MetricCard title="STATUS" value="RUNNING" status="RUNNING" />);
    const card = screen.getByText('STATUS').closest('.metric-card');
    expect(card).toHaveStyle({ borderLeftColor: '#00C851' });
  });

  test('renders with health score', () => {
    render(<MetricCard title="HEALTH" value={94} unit="%" healthScore={94} />);
    expect(screen.getByText('HEALTHY')).toBeInTheDocument();
  });

  test('renders trend indicator', () => {
    render(<MetricCard title="SPEED" value={3000} unit="RPM" trend="up" />);
    expect(screen.getByText('↑')).toBeInTheDocument();
  });
});

describe('StatusBadge', () => {
  test('renders with severity color', () => {
    render(<StatusBadge label="HIGH" severity="HIGH" />);
    const badge = screen.getByText('HIGH');
    expect(badge).toHaveStyle({ backgroundColor: 'rgba(248, 81, 73, 0.125)', color: '#f85149' });
  });

  test('renders with status color', () => {
    render(<StatusBadge label="RUNNING" status="RUNNING" />);
    const badge = screen.getByText('RUNNING');
    expect(badge).toHaveStyle({ backgroundColor: 'rgba(0, 200, 81, 0.125)', color: '#00C851' });
  });
});

describe('ConnectionStatus', () => {
  test('shows connected status', () => {
    render(<ConnectionStatus status="connected" lastMessageTime={Date.now()} />);
    expect(screen.getByText('CONNECTED')).toBeInTheDocument();
    expect(screen.getByText('Last update:')).toBeInTheDocument();
  });

  test('shows disconnected status', () => {
    render(<ConnectionStatus status="disconnected" />);
    expect(screen.getByText('DISCONNECTED')).toBeInTheDocument();
  });

  test('shows connecting status', () => {
    render(<ConnectionStatus status="connecting" />);
    expect(screen.getByText('CONNECTING...')).toBeInTheDocument();
  });
});