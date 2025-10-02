/**
 * Commercial View KPI Dashboard - Core Engine
 * Main class for managing and analyzing commercial KPIs
 */

import {
  KPIMetric,
  DashboardConfig,
  DataSourceConfig,
  TrendDirection,
  KPIStatus,
  TimePeriod,
  DataPoint
} from '../models/types';

/**
 * Main KPI Dashboard Engine
 * Provides comprehensive business intelligence and analytics capabilities
 */
export class CommercialViewEngine {
  private dashboards: Map<string, DashboardConfig> = new Map();
  private dataSources: Map<string, DataSourceConfig> = new Map();

  /**
   * Register a new dashboard configuration
   */
  public registerDashboard(config: DashboardConfig): void {
    this.dashboards.set(config.id, config);
  }

  /**
   * Get dashboard by ID
   */
  public getDashboard(id: string): DashboardConfig | undefined {
    return this.dashboards.get(id);
  }

  /**
   * Get all registered dashboards
   */
  public getAllDashboards(): DashboardConfig[] {
    return Array.from(this.dashboards.values());
  }

  /**
   * Register a data source
   */
  public registerDataSource(config: DataSourceConfig): void {
    this.dataSources.set(config.id, config);
  }

  /**
   * Calculate KPI status based on thresholds
   */
  public calculateKPIStatus(metric: KPIMetric): KPIStatus {
    if (!metric.threshold) {
      return KPIStatus.UNKNOWN;
    }

    const value = metric.currentValue;
    const threshold = metric.threshold;

    if (value >= threshold.excellent) {
      return KPIStatus.EXCELLENT;
    } else if (value >= threshold.good) {
      return KPIStatus.GOOD;
    } else if (value >= threshold.warning) {
      return KPIStatus.WARNING;
    } else if (value >= threshold.critical) {
      return KPIStatus.CRITICAL;
    }

    return KPIStatus.CRITICAL;
  }

  /**
   * Calculate trend direction from historical data
   */
  public calculateTrend(data: DataPoint[], _period: TimePeriod): {
    direction: TrendDirection;
    percentage: number;
  } {
    if (data.length < 2) {
      return { direction: TrendDirection.STABLE, percentage: 0 };
    }

    const sortedData = [...data].sort((a, b) => 
      a.timestamp.getTime() - b.timestamp.getTime()
    );

    const latestValue = sortedData[sortedData.length - 1].value;
    const previousValue = sortedData[sortedData.length - 2].value;

    const percentageChange = ((latestValue - previousValue) / previousValue) * 100;

    let direction: TrendDirection;
    if (Math.abs(percentageChange) < 1) {
      direction = TrendDirection.STABLE;
    } else if (Math.abs(percentageChange) > 20) {
      direction = TrendDirection.VOLATILE;
    } else if (percentageChange > 0) {
      direction = TrendDirection.UP;
    } else {
      direction = TrendDirection.DOWN;
    }

    return { direction, percentage: percentageChange };
  }

  /**
   * Update metric with new data point
   */
  public updateMetric(dashboardId: string, metricId: string, dataPoint: DataPoint): void {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      throw new Error(`Dashboard ${dashboardId} not found`);
    }

    const metric = dashboard.metrics.find(m => m.id === metricId);
    if (!metric) {
      throw new Error(`Metric ${metricId} not found in dashboard ${dashboardId}`);
    }

    metric.historicalData.push(dataPoint);
    metric.currentValue = dataPoint.value;
    
    const trend = this.calculateTrend(metric.historicalData, metric.trend.comparisonPeriod);
    metric.trend.direction = trend.direction;
    metric.trend.percentage = trend.percentage;
    
    metric.status = this.calculateKPIStatus(metric);
  }

  /**
   * Get metrics by category
   */
  public getMetricsByCategory(dashboardId: string, category: string): KPIMetric[] {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return [];
    }

    return dashboard.metrics.filter(m => m.category === category);
  }

  /**
   * Get metrics by status
   */
  public getMetricsByStatus(dashboardId: string, status: KPIStatus): KPIMetric[] {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return [];
    }

    return dashboard.metrics.filter(m => m.status === status);
  }

  /**
   * Export dashboard data for external integrations
   */
  public exportDashboard(dashboardId: string): string {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      throw new Error(`Dashboard ${dashboardId} not found`);
    }

    return JSON.stringify(dashboard, null, 2);
  }
}
