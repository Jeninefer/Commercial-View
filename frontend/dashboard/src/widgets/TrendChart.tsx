import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import type { TrendChartProps } from '../types/widgets';

const palette = ['#1c7c7d', '#f4a259', '#3a6ea5', '#d64550'];

const TrendChart: React.FC<TrendChartProps> = ({ series, loading, error }) => {
  const chartData = useMemo(() => {
    const periodMap = new Map<string, Record<string, string | number>>();

    series.forEach((metric) => {
      metric.points.forEach((point) => {
        if (!periodMap.has(point.period)) {
          periodMap.set(point.period, { period: point.period });
        }
        const row = periodMap.get(point.period)!;
        row[`${metric.metricId}-actual`] = point.actual;
        if (typeof point.target === 'number') {
          row[`${metric.metricId}-target`] = point.target;
        }
      });
    });

    return Array.from(periodMap.values()).sort((a, b) =>
      String(a.period).localeCompare(String(b.period)),
    );
  }, [series]);

  if (error) {
    return (
      <div role="alert" className="alert alert--error">
        <strong>Unable to load performance trends.</strong>
        <span>{error}</span>
      </div>
    );
  }

  if (loading) {
    return <div className="chart-placeholder" aria-busy aria-label="Loading chart" />;
  }

  if (!series.length) {
    return <p role="status">No trend data available yet. Upload portfolio data to get started.</p>;
  }

  return (
    <figure className="chart" role="figure" aria-label="Portfolio trend performance">
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={chartData} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d5dce5" />
          <XAxis dataKey="period" stroke="#3a4b68" />
          <YAxis stroke="#3a4b68" tickFormatter={(value) => `${value}`} />
          <Tooltip contentStyle={{ borderRadius: 8, borderColor: '#1c7c7d' }} />
          <Legend />
          {series.map((metric, index) => {
            const color = palette[index % palette.length];
            const targetKey = `${metric.metricId}-target`;
            const hasTarget = metric.points.some((point) => typeof point.target === 'number');

            return (
              <React.Fragment key={metric.metricId}>
                <Line
                  type="monotone"
                  dataKey={`${metric.metricId}-actual`}
                  name={`${metric.label} Actual`}
                  stroke={color}
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
                {hasTarget && (
                  <Line
                    type="monotone"
                    dataKey={targetKey}
                    name={`${metric.label} Target`}
                    stroke={color}
                    strokeDasharray="6 4"
                    strokeWidth={2}
                    dot={false}
                  />
                )}
              </React.Fragment>
            );
          })}
        </LineChart>
      </ResponsiveContainer>
      <figcaption className="chart__caption">
        Multi-metric comparison of origination volume, utilization, and revenue against ABACO targets.
      </figcaption>
    </figure>
  );
};

export default TrendChart;
