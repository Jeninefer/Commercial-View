# API Documentation

## Table of Contents

- [Core Classes](#core-classes)
- [Models and Types](#models-and-types)
- [Integrations](#integrations)
- [Utilities](#utilities)

## Core Classes

### CommercialViewEngine

Main engine class for managing KPI dashboards.

#### Methods

##### `registerDashboard(config: DashboardConfig): void`

Registers a new dashboard configuration.

**Parameters:**
- `config` - Dashboard configuration object

**Example:**
```typescript
const dashboard: DashboardConfig = {
  id: 'main',
  name: 'Main Dashboard',
  description: 'Primary metrics',
  metrics: []
};
engine.registerDashboard(dashboard);
```

##### `getDashboard(id: string): DashboardConfig | undefined`

Retrieves a dashboard by ID.

**Parameters:**
- `id` - Dashboard identifier

**Returns:**
- Dashboard configuration or undefined if not found

##### `updateMetric(dashboardId: string, metricId: string, dataPoint: DataPoint): void`

Updates a metric with a new data point.

**Parameters:**
- `dashboardId` - Dashboard identifier
- `metricId` - Metric identifier
- `dataPoint` - New data point to add

**Throws:**
- Error if dashboard or metric not found

##### `calculateKPIStatus(metric: KPIMetric): KPIStatus`

Calculates the status of a KPI based on thresholds.

**Parameters:**
- `metric` - KPI metric object

**Returns:**
- KPI status (EXCELLENT, GOOD, WARNING, CRITICAL, UNKNOWN)

## Models and Types

### KPIMetric

Represents a Key Performance Indicator.

**Properties:**
- `id: string` - Unique identifier
- `name: string` - Display name
- `description: string` - Detailed description
- `category: string` - Metric category
- `unit: string` - Unit of measurement
- `currentValue: number` - Current metric value
- `targetValue?: number` - Target/goal value
- `threshold?: ThresholdConfig` - Status thresholds
- `trend: TrendConfig` - Trend information
- `historicalData: DataPoint[]` - Historical data points
- `status: KPIStatus` - Current status
- `tags?: string[]` - Optional tags

### DashboardConfig

Configuration for a dashboard.

**Properties:**
- `id: string` - Unique identifier
- `name: string` - Dashboard name
- `description: string` - Dashboard description
- `metrics: KPIMetric[]` - Array of metrics
- `refreshInterval?: number` - Refresh rate in milliseconds
- `layout?: LayoutConfig` - Layout configuration

### TimePeriod

Enum for time periods.

**Values:**
- `HOURLY` - Hourly data
- `DAILY` - Daily data
- `WEEKLY` - Weekly data
- `MONTHLY` - Monthly data
- `QUARTERLY` - Quarterly data
- `YEARLY` - Yearly data
- `CUSTOM` - Custom period

### KPIStatus

Enum for KPI status indicators.

**Values:**
- `EXCELLENT` - Exceeding expectations
- `GOOD` - Meeting expectations
- `WARNING` - Below expectations
- `CRITICAL` - Requires immediate attention
- `UNKNOWN` - Status cannot be determined

## Integrations

### AIAnalytics

Provides AI and machine learning capabilities.

#### Methods

##### `predictFutureValues(historicalData: DataPoint[], periodsAhead: number): DataPoint[]`

Predicts future values using time series analysis.

**Parameters:**
- `historicalData` - Array of historical data points
- `periodsAhead` - Number of periods to predict

**Returns:**
- Array of predicted data points with confidence metadata

**Example:**
```typescript
const predictions = aiAnalytics.predictFutureValues(metric.historicalData, 7);
```

##### `detectAnomalies(data: DataPoint[], threshold?: number): DataPoint[]`

Detects anomalous data points.

**Parameters:**
- `data` - Array of data points to analyze
- `threshold` - Z-score threshold (default: 2)

**Returns:**
- Array of anomalous data points

##### `generateInsights(metrics: KPIMetric[]): string[]`

Generates AI-powered insights from metrics.

**Parameters:**
- `metrics` - Array of KPI metrics

**Returns:**
- Array of insight strings

##### `calculateCorrelation(metric1: KPIMetric, metric2: KPIMetric): number`

Calculates correlation coefficient between two metrics.

**Parameters:**
- `metric1` - First metric
- `metric2` - Second metric

**Returns:**
- Correlation coefficient (-1 to 1)

### IntegrationManager

Manages external system integrations.

#### Methods

##### `registerIntegration(config: IntegrationConfig, integration: IIntegration): void`

Registers a new integration.

**Parameters:**
- `config` - Integration configuration
- `integration` - Integration implementation

##### `connect(integrationId: string): Promise<boolean>`

Connects to an integration.

**Parameters:**
- `integrationId` - Integration identifier

**Returns:**
- Promise resolving to connection status

##### `fetchData(integrationId: string, query?: unknown): Promise<DataPoint[]>`

Fetches data from an integration.

**Parameters:**
- `integrationId` - Integration identifier
- `query` - Optional query parameters

**Returns:**
- Promise resolving to array of data points

### IIntegration Interface

Base interface for integrations.

**Methods:**
- `connect(): Promise<boolean>` - Establish connection
- `disconnect(): Promise<void>` - Close connection
- `fetchData(query?: unknown): Promise<DataPoint[]>` - Fetch data
- `isConnected(): boolean` - Check connection status

## Utilities

### Helper Functions

##### `formatNumber(value: number, decimals?: number): string`

Formats numbers with thousand separators.

##### `formatCurrency(value: number, currency?: string): string`

Formats currency values.

##### `formatPercentage(value: number, decimals?: number): string`

Formats percentage values.

##### `calculateAverage(data: DataPoint[]): number`

Calculates average of data points.

##### `calculateMedian(data: DataPoint[]): number`

Calculates median of data points.

##### `filterByTimePeriod(data: DataPoint[], period: TimePeriod): DataPoint[]`

Filters data by time period.

##### `generateSampleData(count: number, baseValue?: number, volatility?: number): DataPoint[]`

Generates sample data for testing.

## Configuration

### ConfigManager

Manages application configuration.

#### Methods

##### `load(config: AppConfig): void`

Loads configuration.

##### `getConfig(): AppConfig`

Gets current configuration.

##### `static getDefaultConfig(): AppConfig`

Returns default configuration.

##### `exportConfig(): string`

Exports configuration to JSON string.

## Error Handling

All methods that can fail will throw descriptive errors. Always wrap calls in try-catch blocks:

```typescript
try {
  const dashboard = engine.getDashboard('non-existent');
} catch (error) {
  console.error('Error:', error.message);
}
```

## TypeScript Types

All types are fully typed. Enable strict mode in your `tsconfig.json` for best experience:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true
  }
}
```
