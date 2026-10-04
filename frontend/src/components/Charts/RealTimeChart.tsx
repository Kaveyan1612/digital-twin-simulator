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
import type { HistoricalDataPoint } from '../../types/twin';
import { formatTimestamp } from '../../utils/formatting';

interface RealTimeChartProps {
  data: HistoricalDataPoint[];
  dataKey: keyof HistoricalDataPoint;
  name: string;
  unit: string;
  color: string;
  height?: number;
  showGrid?: boolean;
  yDomain?: [number, number];
  maxPoints?: number;
}

export const RealTimeChart: React.FC<RealTimeChartProps> = ({
  data,
  dataKey,
  name,
  unit,
  color,
  height = 200,
  showGrid = true,
  yDomain,
  maxPoints = 1000,
}) => {
  const displayData = data.slice(-maxPoints).map((d, i) => ({
    ...d,
    index: i,
    time: formatTimestamp(d.timestamp),
  }));

  const formattedDataKey = dataKey as string;

  return (
    <div className="chart-container" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />}
          <XAxis
            dataKey="time"
            tick={{ fill: '#888', fontSize: 10 }}
            axisLine={{ stroke: '#333' }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#888', fontSize: 10 }}
            axisLine={{ stroke: '#333' }}
            tickLine={false}
            domain={yDomain || ['auto', 'auto']}
            tickFormatter={(value) => `${value}${unit}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e1e1e',
              border: '1px solid #333',
              borderRadius: '4px',
            }}
            labelFormatter={(_, payload) => payload[0]?.payload?.time || ''}
            formatter={(value: number) => [`${value.toFixed(2)} ${unit}`, name]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={formattedDataKey}
            name={`${name} (${unit})`}
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, strokeWidth: 2 }}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

interface MultiLineChartProps {
  data: HistoricalDataPoint[];
  lines: Array<{
    dataKey: keyof HistoricalDataPoint;
    name: string;
    unit: string;
    color: string;
  }>;
  height?: number;
  showGrid?: boolean;
  maxPoints?: number;
}

export const MultiLineChart: React.FC<MultiLineChartProps> = ({
  data,
  lines,
  height = 250,
  showGrid = true,
  maxPoints = 1000,
}) => {
  const displayData = data.slice(-maxPoints).map((d, i) => ({
    ...d,
    index: i,
    time: formatTimestamp(d.timestamp),
  }));

  return (
    <div className="chart-container" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={displayData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />}
          <XAxis
            dataKey="time"
            tick={{ fill: '#888', fontSize: 10 }}
            axisLine={{ stroke: '#333' }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#888', fontSize: 10 }}
            axisLine={{ stroke: '#333' }}
            tickLine={false}
            tickFormatter={(value) => value.toFixed(1)}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e1e1e',
              border: '1px solid #333',
              borderRadius: '4px',
            }}
            labelFormatter={(_, payload) => payload[0]?.payload?.time || ''}
          />
          <Legend />
          {lines.map((line, index) => (
            <Line
              key={index}
              type="monotone"
              dataKey={line.dataKey as string}
              name={`${line.name} (${line.unit})`}
              stroke={line.color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, strokeWidth: 2 }}
              animationDuration={300}
              yAxisId={index === 0 ? 0 : 1}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};