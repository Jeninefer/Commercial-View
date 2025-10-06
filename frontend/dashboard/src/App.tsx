import React, { useMemo } from 'react';
import DashboardLayout from './layouts/DashboardLayout';
import KpiGrid from './widgets/KpiGrid';
import TrendChart from './widgets/TrendChart';
import RiskDistributionTable from './widgets/RiskDistributionTable';
import ExposureTable from './widgets/ExposureTable';
import CsvUploader from './widgets/CsvUploader';
import { useExecutiveSummary } from './hooks/useExecutiveSummary';
import { usePortfolioTrends } from './hooks/usePortfolioTrends';
import { useRiskExposure } from './hooks/useRiskExposure';
import { useCsvIngestion } from './hooks/useCsvIngestion';
import './styles/dashboard.css';

const App: React.FC = () => {
  const {
    data: executiveSummary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useExecutiveSummary();
  const {
    data: trends,
    isLoading: trendsLoading,
    error: trendsError,
  } = usePortfolioTrends();
  const {
    data: riskExposure,
    isLoading: riskLoading,
    error: riskError,
  } = useRiskExposure();

  const { state: csvState, ingestCsv, resetError } = useCsvIngestion();

  const lastUpdated = useMemo(() => executiveSummary?.meta.lastUpdated ?? '', [
    executiveSummary,
  ]);

  return (
    <DashboardLayout lastUpdated={lastUpdated} csvState={csvState}>
      <section className="dashboard-section" aria-labelledby="kpi-overview-heading">
        <header className="section-header">
          <div>
            <h2 id="kpi-overview-heading">Portfolio KPI Overview</h2>
            <p className="section-subtitle">
              Real-time visibility into asset quality, profitability, and pipeline momentum.
            </p>
          </div>
          <CsvUploader
            onUpload={ingestCsv}
            state={csvState}
            onDismissError={resetError}
          />
        </header>
        <KpiGrid
          metrics={executiveSummary?.data.metrics ?? []}
          loading={summaryLoading}
          error={summaryError?.message}
        />
      </section>

      <section className="dashboard-section" aria-labelledby="trend-analysis-heading">
        <header className="section-header">
          <div>
            <h2 id="trend-analysis-heading">Portfolio Performance Trends</h2>
            <p className="section-subtitle">
              Track originations, utilization, and revenue trajectories against targets.
            </p>
          </div>
        </header>
        <TrendChart
          series={trends?.data ?? []}
          loading={trendsLoading}
          error={trendsError?.message}
        />
      </section>

      <section className="dashboard-section" aria-labelledby="risk-insights-heading">
        <header className="section-header">
          <div>
            <h2 id="risk-insights-heading">Risk Distribution</h2>
            <p className="section-subtitle">
              Understand concentration, delinquency, and expected loss by segment.
            </p>
          </div>
        </header>
        <RiskDistributionTable
          rows={riskExposure?.data.riskDistribution ?? []}
          loading={riskLoading}
          error={riskError?.message}
        />
      </section>

      <section className="dashboard-section" aria-labelledby="exposure-table-heading">
        <header className="section-header">
          <div>
            <h2 id="exposure-table-heading">Top Exposures</h2>
            <p className="section-subtitle">
              Prioritize follow-ups across the largest, riskiest positions.
            </p>
          </div>
        </header>
        <ExposureTable
          rows={riskExposure?.data.topExposures ?? []}
          loading={riskLoading}
          error={riskError?.message}
        />
      </section>
    </DashboardLayout>
  );
};

export default App;
