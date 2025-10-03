/**
 * Core Types and Interfaces for Commercial View KPI Dashboard
 * Professional-grade type definitions for business intelligence metrics
 */

/**
 * Time period for KPI measurement
 */
export enum TimePeriod {
  HOURLY = 'hourly',
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  YEARLY = 'yearly',
  CUSTOM = 'custom'
}

/**
 * KPI trend direction
 */
export enum TrendDirection {
  UP = 'up',
  DOWN = 'down',
  STABLE = 'stable',
  VOLATILE = 'volatile'
}

/**
 * KPI status indicator
 */
export enum KPIStatus {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  WARNING = 'warning',
  CRITICAL = 'critical',
  UNKNOWN = 'unknown'
}

/**
 * Base data point interface
 */
export interface DataPoint {
  timestamp: Date;
  value: number;
  metadata?: Record<string, unknown>;
}

/**
 * KPI metric configuration
 */
export interface KPIMetric {
  id: string;
  name: string;
  description: string;
  category: string;
  unit: string;
  currentValue: number;
  targetValue?: number;
  threshold?: {
    excellent: number;
    good: number;
    warning: number;
    critical: number;
  };
  trend: {
    direction: TrendDirection;
    percentage: number;
    comparisonPeriod: TimePeriod;
  };
  historicalData: DataPoint[];
  status: KPIStatus;
  tags?: string[];
}

/**
 * Dashboard configuration
 */
export interface DashboardConfig {
  id: string;
  name: string;
  description: string;
  metrics: KPIMetric[];
  refreshInterval?: number;
  layout?: {
    columns: number;
    rows: number;
  };
  filters?: Record<string, unknown>;
}

/**
 * Data source configuration
 */
export interface DataSourceConfig {
  id: string;
  name: string;
  type: 'api' | 'database' | 'file' | 'stream' | 'ai-model';
  connectionString?: string;
  authentication?: {
    type: 'none' | 'basic' | 'oauth' | 'apikey' | 'token';
    credentials?: Record<string, string>;
  };
  refreshRate?: number;
  enabled: boolean;
}

/**
 * AI/ML prediction configuration
 */
export interface AIPredictionConfig {
  modelId: string;
  modelType: 'regression' | 'classification' | 'timeseries' | 'anomaly-detection';
  features: string[];
  confidenceThreshold: number;
  enabled: boolean;
}

/**
 * Integration configuration for external systems
 */
export interface IntegrationConfig {
  id: string;
  name: string;
  type: string;
  endpoint?: string;
  apiKey?: string;
  enabled: boolean;
  settings?: Record<string, unknown>;
}

/**
 * Commercial analytics report
 */
export interface CommercialReport {
  id: string;
  title: string;
  generatedAt: Date;
  period: TimePeriod;
  metrics: KPIMetric[];
  summary: {
    totalRevenue?: number;
    growth?: number;
    topPerformers?: string[];
    insights?: string[];
  };
  recommendations?: string[];
}
