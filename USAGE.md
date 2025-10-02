# Commercial-View Usage Guide

A comprehensive guide to using the Commercial-View KPI Dashboard system for professional business intelligence.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Dashboard Management](#dashboard-management)
4. [KPI Metrics](#kpi-metrics)
5. [AI Analytics](#ai-analytics)
6. [Integrations](#integrations)
7. [Best Practices](#best-practices)
8. [Advanced Usage](#advanced-usage)

---

## Getting Started

### Installation

```bash
npm install commercial-view
```

### Quick Start

```typescript
import { CommercialViewEngine } from 'commercial-view';

const engine = new CommercialViewEngine();
```

---

## Core Concepts

### 1. Dashboards

Dashboards are containers for related KPI metrics. They organize your data and provide a cohesive view of business performance.

**Key Properties:**
- `id`: Unique identifier
- `name`: Display name
- `description`: Purpose and context
- `metrics`: Array of KPI metrics
- `refreshInterval`: Update frequency (milliseconds)
- `layout`: Visual organization

### 2. KPI Metrics

Individual performance indicators that measure specific aspects of your business.

**Key Properties:**
- `currentValue`: Latest measurement
- `targetValue`: Goal or objective
- `threshold`: Status boundaries
- `trend`: Direction and magnitude
- `historicalData`: Time-series data

### 3. Data Points

Individual measurements with timestamp and value.

**Structure:**
```typescript
{
  timestamp: Date,
  value: number,
  metadata?: object
}
```

---

## Dashboard Management

### Creating a Dashboard

```typescript
import { DashboardConfig, CommercialViewEngine } from 'commercial-view';

const dashboard: DashboardConfig = {
  id: 'my-dashboard',
  name: 'My Business Dashboard',
  description: 'Key business metrics',
  metrics: [],
  refreshInterval: 60000,
  layout: { columns: 3, rows: 2 }
};

const engine = new CommercialViewEngine();
engine.registerDashboard(dashboard);
```

### Retrieving Dashboards

```typescript
// Get specific dashboard
const dashboard = engine.getDashboard('my-dashboard');

// Get all dashboards
const allDashboards = engine.getAllDashboards();
```

### Exporting Dashboard Data

```typescript
const jsonData = engine.exportDashboard('my-dashboard');
console.log(jsonData); // JSON string
```

---

## KPI Metrics

### Defining a Metric

```typescript
import { KPIMetric, TimePeriod, KPIStatus, TrendDirection } from 'commercial-view';

const metric: KPIMetric = {
  id: 'revenue',
  name: 'Monthly Revenue',
  description: 'Total monthly revenue',
  category: 'Financial',
  unit: 'USD',
  currentValue: 100000,
  targetValue: 120000,
  threshold: {
    excellent: 120000,
    good: 100000,
    warning: 80000,
    critical: 60000
  },
  trend: {
    direction: TrendDirection.UP,
    percentage: 10.5,
    comparisonPeriod: TimePeriod.MONTHLY
  },
  historicalData: [],
  status: KPIStatus.GOOD,
  tags: ['revenue', 'primary']
};
```

### Updating Metrics

```typescript
const newDataPoint = {
  timestamp: new Date(),
  value: 105000,
  metadata: { source: 'payment-api' }
};

engine.updateMetric('dashboard-id', 'metric-id', newDataPoint);
```

### Querying Metrics

```typescript
// By category
const financialMetrics = engine.getMetricsByCategory('dashboard-id', 'Financial');

// By status
const criticalMetrics = engine.getMetricsByStatus('dashboard-id', KPIStatus.CRITICAL);
```

### Status Calculation

Status is automatically calculated based on thresholds:

```typescript
const status = engine.calculateKPIStatus(metric);
// Returns: EXCELLENT, GOOD, WARNING, CRITICAL, or UNKNOWN
```

---

## AI Analytics

### Setting Up AI Analytics

```typescript
import { AIAnalytics } from 'commercial-view';

const aiAnalytics = new AIAnalytics();
```

### Predictive Analytics

```typescript
// Predict future values
const predictions = aiAnalytics.predictFutureValues(
  metric.historicalData,
  7  // Predict 7 periods ahead
);

predictions.forEach(pred => {
  console.log(`Date: ${pred.timestamp}`);
  console.log(`Predicted: ${pred.value}`);
  console.log(`Confidence: ${pred.metadata?.confidence}`);
});
```

### Anomaly Detection

```typescript
// Detect unusual data points
const anomalies = aiAnalytics.detectAnomalies(
  metric.historicalData,
  2  // Z-score threshold
);

console.log(`Found ${anomalies.length} anomalies`);
```

### Insight Generation

```typescript
// Generate AI insights
const insights = aiAnalytics.generateInsights([metric1, metric2]);

insights.forEach(insight => {
  console.log(`💡 ${insight}`);
});
```

### Correlation Analysis

```typescript
// Find relationships between metrics
const correlation = aiAnalytics.calculateCorrelation(metric1, metric2);

if (correlation > 0.7) {
  console.log('Strong positive correlation');
} else if (correlation < -0.7) {
  console.log('Strong negative correlation');
}
```

---

## Integrations

### Setting Up Integration Manager

```typescript
import { IntegrationManager, APIIntegration } from 'commercial-view';

const integrationManager = new IntegrationManager();
```

### API Integration

```typescript
const apiIntegration = new APIIntegration(
  'https://api.example.com/data',
  'your-api-key'
);

integrationManager.registerIntegration(
  {
    id: 'external-api',
    name: 'External Data API',
    type: 'api',
    enabled: true,
    endpoint: 'https://api.example.com/data',
    apiKey: 'your-api-key'
  },
  apiIntegration
);
```

### Fetching Data

```typescript
// Connect and fetch
await integrationManager.connect('external-api');
const data = await integrationManager.fetchData('external-api', {
  startDate: '2024-01-01',
  endDate: '2024-12-31'
});
```

### Repository Integration

```typescript
import { RepositoryIntegration } from 'commercial-view';

const repoIntegration = new RepositoryIntegration(
  'https://github.com/org/repo',
  'github-token'
);

integrationManager.registerIntegration(
  {
    id: 'github',
    name: 'GitHub Metrics',
    type: 'repository',
    enabled: true
  },
  repoIntegration
);
```

---

## Best Practices

### 1. Data Quality

```typescript
import { validateDataQuality } from 'commercial-view';

const validation = validateDataQuality(metric.historicalData);
if (!validation.isValid) {
  console.warn('Data quality issues:', validation.issues);
}
```

### 2. Time Period Filtering

```typescript
import { filterByTimePeriod, TimePeriod } from 'commercial-view';

const recentData = filterByTimePeriod(
  metric.historicalData,
  TimePeriod.MONTHLY
);
```

### 3. Statistical Analysis

```typescript
import { calculateAverage, calculateMedian, calculateStandardDeviation } from 'commercial-view';

const avg = calculateAverage(metric.historicalData);
const median = calculateMedian(metric.historicalData);
const stdDev = calculateStandardDeviation(metric.historicalData);

console.log(`Average: ${avg}`);
console.log(`Median: ${median}`);
console.log(`Std Dev: ${stdDev}`);
```

### 4. Formatting Output

```typescript
import { formatNumber, formatCurrency, formatPercentage } from 'commercial-view';

console.log(formatCurrency(metric.currentValue));     // $100,000.00
console.log(formatNumber(metric.currentValue));       // 100,000.00
console.log(formatPercentage(metric.trend.percentage)); // 10.5%
```

### 5. Configuration Management

```typescript
import { ConfigManager } from 'commercial-view';

const configManager = new ConfigManager();
const config = ConfigManager.getDefaultConfig();

config.settings.enableAI = true;
config.settings.logLevel = 'info';

configManager.load(config);
```

---

## Advanced Usage

### Custom Integration Implementation

```typescript
import { IIntegration, DataPoint } from 'commercial-view';

class CustomIntegration implements IIntegration {
  private connected = false;

  async connect(): Promise<boolean> {
    // Your connection logic
    this.connected = true;
    return true;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }

  async fetchData(query?: unknown): Promise<DataPoint[]> {
    // Your data fetching logic
    return [];
  }

  isConnected(): boolean {
    return this.connected;
  }
}
```

### Real-time Monitoring

```typescript
class DashboardMonitor {
  private engine: CommercialViewEngine;
  private intervalId?: NodeJS.Timeout;

  constructor(engine: CommercialViewEngine) {
    this.engine = engine;
  }

  start(dashboardId: string, interval: number = 60000): void {
    this.intervalId = setInterval(() => {
      const dashboard = this.engine.getDashboard(dashboardId);
      const criticalMetrics = this.engine.getMetricsByStatus(
        dashboardId,
        KPIStatus.CRITICAL
      );

      if (criticalMetrics.length > 0) {
        this.alert(criticalMetrics);
      }
    }, interval);
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  private alert(metrics: KPIMetric[]): void {
    console.error('CRITICAL ALERT:', metrics.map(m => m.name));
  }
}
```

### Batch Data Processing

```typescript
async function processBatchData(
  engine: CommercialViewEngine,
  dashboardId: string,
  metricId: string,
  dataPoints: DataPoint[]
): Promise<void> {
  for (const point of dataPoints) {
    engine.updateMetric(dashboardId, metricId, point);
    
    // Add delay to prevent overwhelming the system
    await new Promise(resolve => setTimeout(resolve, 10));
  }
}
```

### Error Handling

```typescript
try {
  const dashboard = engine.getDashboard('non-existent');
  if (!dashboard) {
    throw new Error('Dashboard not found');
  }
} catch (error) {
  console.error('Error:', error.message);
  // Handle error appropriately
}
```

---

## Performance Tips

1. **Use appropriate refresh intervals** - Don't update too frequently
2. **Limit historical data** - Keep only necessary data points
3. **Batch updates** - Update multiple metrics together when possible
4. **Cache frequently accessed data** - Reduce redundant calculations
5. **Monitor memory usage** - Clean up old data periodically

---

## Troubleshooting

### Common Issues

**Issue: Metric status always UNKNOWN**
- Check threshold configuration
- Ensure currentValue is set

**Issue: Trends not updating**
- Verify historical data exists
- Check comparisonPeriod setting

**Issue: Integration connection fails**
- Verify credentials
- Check network connectivity
- Review API endpoint

**Issue: Predictions inaccurate**
- Increase historical data points
- Check data quality
- Review volatility settings

---

## Next Steps

- Explore the [examples](./examples/) directory
- Read the [API documentation](./API.md)
- Check the [changelog](./CHANGELOG.md) for updates
- Join the community discussions

---

**Need help?** Open an issue on GitHub or contact the maintainers.
