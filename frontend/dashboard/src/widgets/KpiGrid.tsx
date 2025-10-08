import React from 'react';
import classNames from 'classnames';
import type { KpiGridProps } from '../types/widgets';
import { formatMetricValue } from '../utils/formatters';

const statusClassMap = {
  onTrack: 'kpi-tile--success',
  atRisk: 'kpi-tile--warning',
  offTrack: 'kpi-tile--critical',
} as const;

const KpiGrid: React.FC<KpiGridProps> = ({ metrics, loading, error }) => {
  if (error) {
    return (
      <div role="alert" className="alert alert--error">
        <strong>We couldn&apos;t load KPI metrics.</strong>
        <span>{error}</span>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="kpi-grid" aria-busy>
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="kpi-tile kpi-tile--loading" aria-hidden />
        ))}
      </div>
    );
  }

  return (
    <div className="kpi-grid" role="list">
      {metrics.map((metric) => (
        <article
          key={metric.id}
          role="listitem"
          className={classNames('kpi-tile', statusClassMap[metric.status])}
          aria-label={`${metric.label} ${formatMetricValue(metric.value, metric.unit)}`}
        >
          <header className="kpi-tile__header">
            <span className="kpi-tile__label">{metric.label}</span>
            {metric.target && (
              <span className="kpi-tile__target">Target: {formatMetricValue(metric.target, metric.unit)}</span>
            )}
          </header>
          <div className="kpi-tile__value">{formatMetricValue(metric.value, metric.unit)}</div>
          <footer className="kpi-tile__footer">
            <span
              className={classNames('kpi-tile__trend', {
                'kpi-tile__trend--positive': metric.change >= 0,
                'kpi-tile__trend--negative': metric.change < 0,
              })}
            >
              {metric.changeLabel}
            </span>
          </footer>
        </article>
      ))}
    </div>
  );
};

export default KpiGrid;
