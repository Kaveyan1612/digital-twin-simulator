import React from 'react';
import { formatTimestamp } from '../../utils/formatting';

interface ConnectionStatusProps {
  status: 'connected' | 'disconnected' | 'connecting';
  lastMessageTime?: number;
  clientCount?: number;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  status,
  lastMessageTime,
  clientCount,
}) => {
  const statusConfig = {
    connected: { label: 'CONNECTED', color: '#00C851', dotColor: '#00C851' },
    disconnected: { label: 'DISCONNECTED', color: '#FF4444', dotColor: '#FF4444' },
    connecting: { label: 'CONNECTING...', color: '#FF8800', dotColor: '#FF8800' },
  };

  const config = statusConfig[status];

  return (
    <div className="connection-status">
      <div className="connection-indicator">
        <span 
          className="connection-dot" 
          style={{ backgroundColor: config.dotColor }}
        />
        <span className="connection-label" style={{ color: config.color }}>
          {config.label}
        </span>
      </div>
      {lastMessageTime && (
        <span className="last-message">
          Last update: {formatTimestamp(lastMessageTime)}
        </span>
      )}
      {clientCount !== undefined && (
        <span className="client-count">
          Clients: {clientCount}
        </span>
      )}
    </div>
  );
};