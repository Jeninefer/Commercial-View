# Commercial-View Examples

This directory contains comprehensive examples demonstrating the capabilities of the Commercial-View KPI Dashboard.

## Available Examples

### 1. Basic Example (`basic-example.ts`)

Demonstrates fundamental features:
- Creating and registering dashboards
- Defining KPI metrics with thresholds
- Updating metrics with new data
- Querying metrics by category and status
- Exporting dashboard data

**Run:**
```bash
npx ts-node examples/basic-example.ts
```

**What you'll learn:**
- Dashboard configuration
- Metric definition and thresholds
- Status calculation
- Trend analysis
- Data organization

---

### 2. AI Analytics Example (`ai-analytics-example.ts`)

Showcases AI-powered features:
- Time series prediction
- Anomaly detection
- Insight generation
- Correlation analysis
- Confidence scoring

**Run:**
```bash
npx ts-node examples/ai-analytics-example.ts
```

**What you'll learn:**
- Predictive analytics
- Anomaly detection algorithms
- Statistical correlation
- AI-powered recommendations
- Confidence intervals

---

### 3. Integration Example (`integration-example.ts`)

Demonstrates external system connectivity:
- API integrations
- Repository connections
- Multi-source dashboards
- Integration management
- Best practices

**Run:**
```bash
npx ts-node examples/integration-example.ts
```

**What you'll learn:**
- Connecting to external APIs
- Repository metric tracking
- Integration lifecycle management
- Error handling
- Security best practices

---

## Prerequisites

Install dependencies:
```bash
npm install
npm install -g ts-node  # For running TypeScript examples
```

Build the project:
```bash
npm run build
```

## Running Examples

### Option 1: Using ts-node (Recommended)
```bash
npx ts-node examples/basic-example.ts
npx ts-node examples/ai-analytics-example.ts
npx ts-node examples/integration-example.ts
```

### Option 2: Compile and Run
```bash
# Compile examples
npx tsc examples/*.ts --outDir /tmp/examples --esModuleInterop --moduleResolution node

# Run compiled examples
node /tmp/examples/examples/basic-example.js
node /tmp/examples/examples/ai-analytics-example.js
node /tmp/examples/examples/integration-example.js
```

## Example Output

Each example produces formatted console output showing:
- ✓ Success indicators
- ⚠ Warning messages
- Formatted metrics and statistics
- AI-generated insights
- Integration status

## Creating Your Own Examples

Use these examples as templates for your own use cases:

1. **Import the necessary components:**
```typescript
import {
  CommercialViewEngine,
  AIAnalytics,
  IntegrationManager,
  KPIMetric,
  // ... other imports
} from '../src/index';
```

2. **Initialize components:**
```typescript
const engine = new CommercialViewEngine();
const aiAnalytics = new AIAnalytics();
```

3. **Configure your dashboard:**
```typescript
const dashboard = {
  id: 'my-dashboard',
  name: 'My Dashboard',
  description: 'Custom metrics',
  metrics: []
};
```

4. **Add metrics and analyze:**
```typescript
// Add your metrics
// Run analysis
// Generate insights
```

## Common Patterns

### Pattern 1: Real-time Monitoring
```typescript
setInterval(() => {
  const newData = fetchLatestData();
  engine.updateMetric(dashboardId, metricId, newData);
}, 60000); // Update every minute
```

### Pattern 2: Batch Processing
```typescript
const historicalData = loadHistoricalData();
historicalData.forEach(point => {
  engine.updateMetric(dashboardId, metricId, point);
});
```

### Pattern 3: Multi-Dashboard Management
```typescript
const dashboards = ['sales', 'operations', 'finance'];
dashboards.forEach(id => {
  const dashboard = engine.getDashboard(id);
  // Process each dashboard
});
```

## Troubleshooting

### TypeScript Compilation Errors
- Ensure `tsconfig.json` is properly configured
- Check that all dependencies are installed
- Verify TypeScript version compatibility

### Runtime Errors
- Check that the build is up to date (`npm run build`)
- Verify all required imports are available
- Review error messages for missing dependencies

### Integration Issues
- Verify API keys and credentials
- Check network connectivity
- Review integration configuration

## Best Practices

1. **Always validate data before processing**
2. **Handle errors gracefully**
3. **Use appropriate refresh intervals**
4. **Monitor prediction confidence**
5. **Keep historical data within reasonable limits**
6. **Document custom metrics and thresholds**
7. **Test integrations before production use**

## Additional Resources

- [Main README](../README.md) - Project overview
- [API Documentation](../API.md) - Complete API reference
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

## Need Help?

- Open an issue on GitHub
- Check the API documentation
- Review the inline code comments
- Contact the maintainers

---

**Happy analyzing!** 📊
