export type MetricStatus = 'onTrack' | 'atRisk' | 'offTrack';

export type MetricUnit = 'currency' | 'percentage' | 'count' | 'ratio';

export interface KpiMetric {
  id: string;
  label: string;
  value: number;
  change: number;
  changeLabel: string;
  status: MetricStatus;
  unit: MetricUnit;
  target?: number;
}

export interface ExecutiveSummary {
  metrics: KpiMetric[];
  insights: string[];
}

export interface PortfolioTrendPoint {
  period: string;
  actual: number;
  target?: number;
  benchmark?: number;
}

export interface PortfolioTrendSeries {
  metricId: string;
  label: string;
  unit: MetricUnit;
  points: PortfolioTrendPoint[];
}

export interface RiskDistributionRow {
  segment: string;
  outstanding: number;
  delinquencyRate: number;
  lossGivenDefault: number;
  riskLevel: 'Low' | 'Moderate' | 'Elevated' | 'Critical';
}

export interface ExposureRow {
  borrower: string;
  relationshipManager: string;
  outstanding: number;
  riskScore: number;
  industry: string;
  nextReview: string;
}

export interface RiskExposure {
  riskDistribution: RiskDistributionRow[];
  topExposures: ExposureRow[];
}
