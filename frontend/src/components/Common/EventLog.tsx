import React from 'react';
import { useTwinStore } from '../../store/twinStore';
import { formatTimestamp } from '../../utils/formatting';

export const EventLog: React.FC = () => {
  const events = useTwinStore(s => s.eventLog);

  if (events.length === 0) {
    return (
      <div className="event-log">
        <h3>Event Log</h3>
        <div className="no-events">No events yet</div>
      </div>
    );
  }

  return (
    <div className="event-log">
      <h3>Event Log</h3>
      <div className="event-list">
        {events.map((event, index) => (
          <div key={index} className={`event-item event-${event.type}`}>
            <span className="event-time">{formatTimestamp(event.timestamp)}</span>
            <span className="event-message">{event.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};