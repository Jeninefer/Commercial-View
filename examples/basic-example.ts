/**
 * Basic Example: Getting Started with Commercial View
 * This example demonstrates the fundamental features of the KPI dashboard
 */

import {
  CommercialViewEngine,
  DashboardConfig,
  KPIMetric,
  TimePeriod,
  KPIStatus,
  TrendDirection,
  generateSampleData
} from '../src/index';

// Initialize the engine
const engine = new CommercialViewEngine();

// Create a sample dashboard configuration
const dashboard: DashboardConfig = {
  id: 'sales-dashboard',
  name: 'Sales Performance Dashboard',
  description: 'Track key sales metrics and performance indicators',
  metrics: [],
  refreshInterval: 60000, // 60 seconds
  layout: {
    columns: 3,
    rows: 2
  }
};

// Create sample KPI metrics
const metrics: KPIMetric[] = [
  {
    id: 'monthly-revenue',
    name: 'Monthly Revenue',
    description: 'Total revenue for the current month',
    category: 'Financial',
    unit: 'USD',
    currentValue: 125000,
    targetValue: 150000,
    threshold: {
      excellent: 150000,
      good: 120000,
      warning: 100000,
      critical: 80000
    },
    trend: {
      direction: TrendDirection.UP,
      percentage: 15.5,
      comparisonPeriod: TimePeriod.MONTHLY
    },
    historicalData: generateSampleData(30, 120000, 0.05),
    status: KPIStatus.GOOD,
    tags: ['revenue', 'financial', 'primary']
  },
  {
    id: 'conversion-rate',
    name: 'Conversion Rate',
    description: 'Percentage of leads converted to customers',
    category: 'Sales',
    unit: '%',
    currentValue: 8.5,
    targetValue: 10.0,
    threshold: {
      excellent: 10,
      good: 8,
      warning: 6,
      critical: 4
    },
    trend: {
      direction: TrendDirection.UP,
      percentage: 5.2,
      comparisonPeriod: TimePeriod.WEEKLY
    },
    historicalData: generateSampleData(30, 8, 0.1),
    status: KPIStatus.GOOD,
    tags: ['conversion', 'sales']
  },
  {
    id: 'customer-satisfaction',
    name: 'Customer Satisfaction Score',
    description: 'Average customer satisfaction rating',
    category: 'Customer',
    unit: 'score',
    currentValue: 4.7,
    targetValue: 4.8,
    threshold: {
      excellent: 4.8,
      good: 4.5,
      warning: 4.0,
      critical: 3.5
    },
    trend: {
      direction: TrendDirection.STABLE,
      percentage: 0.8,
      comparisonPeriod: TimePeriod.MONTHLY
    },
    historicalData: generateSampleData(30, 4.6, 0.02),
    status: KPIStatus.GOOD,
    tags: ['satisfaction', 'customer', 'quality']
  }
];

// Add metrics to dashboard
dashboard.metrics = metrics;

// Register the dashboard
engine.registerDashboard(dashboard);

// Demonstrate basic operations
function demonstrateBasicOperations(): void {
  console.log('=== Commercial View - Basic Example ===\n');

  // Get dashboard
  const retrievedDashboard = engine.getDashboard('sales-dashboard');
  console.log(`Dashboard: ${retrievedDashboard?.name}`);
  console.log(`Total Metrics: ${retrievedDashboard?.metrics.length}\n`);

  // Display all metrics
  console.log('Current Metrics:');
  retrievedDashboard?.metrics.forEach(metric => {
    console.log(`\n${metric.name}:`);
    console.log(`  Current Value: ${metric.currentValue} ${metric.unit}`);
    console.log(`  Target Value: ${metric.targetValue} ${metric.unit}`);
    console.log(`  Status: ${metric.status}`);
    console.log(`  Trend: ${metric.trend.direction} (${metric.trend.percentage.toFixed(1)}%)`);
  });

  // Get metrics by category
  console.log('\n\n=== Metrics by Category ===');
  const financialMetrics = engine.getMetricsByCategory('sales-dashboard', 'Financial');
  console.log(`\nFinancial Metrics: ${financialMetrics.length}`);
  financialMetrics.forEach(m => console.log(`  - ${m.name}`));

  const salesMetrics = engine.getMetricsByCategory('sales-dashboard', 'Sales');
  console.log(`\nSales Metrics: ${salesMetrics.length}`);
  salesMetrics.forEach(m => console.log(`  - ${m.name}`));

  // Get metrics by status
  console.log('\n\n=== Metrics by Status ===');
  const goodMetrics = engine.getMetricsByStatus('sales-dashboard', KPIStatus.GOOD);
  console.log(`\nGood Status Metrics: ${goodMetrics.length}`);
  goodMetrics.forEach(m => console.log(`  - ${m.name}`));

  // Update a metric with new data
  console.log('\n\n=== Updating Metric ===');
  const newDataPoint = {
    timestamp: new Date(),
    value: 130000,
    metadata: { note: 'End of month update' }
  };
  
  console.log(`Updating ${metrics[0].name} with new value: ${newDataPoint.value}`);
  engine.updateMetric('sales-dashboard', 'monthly-revenue', newDataPoint);
  
  const updatedMetric = engine.getDashboard('sales-dashboard')?.metrics.find(m => m.id === 'monthly-revenue');
  console.log(`New Current Value: ${updatedMetric?.currentValue}`);
  console.log(`Updated Status: ${updatedMetric?.status}`);
  console.log(`Updated Trend: ${updatedMetric?.trend.direction} (${updatedMetric?.trend.percentage.toFixed(1)}%)`);

  // Export dashboard
  console.log('\n\n=== Export Dashboard ===');
  const exportedData = engine.exportDashboard('sales-dashboard');
  console.log('Dashboard exported successfully (JSON format)');
  console.log(`Export size: ${exportedData.length} characters`);
}

// Run the demonstration
demonstrateBasicOperations();

export { engine, dashboard, metrics };
