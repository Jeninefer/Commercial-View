/**
 * Advanced Example: AI Analytics and Predictions
 * Demonstrates AI-powered features including predictions, anomaly detection, and insights
 */

import {
  CommercialViewEngine,
  AIAnalytics,
  KPIMetric,
  TimePeriod,
  KPIStatus,
  TrendDirection,
  generateSampleData,
  formatNumber,
  formatPercentage
} from '../src/index';

// Initialize components
const engine = new CommercialViewEngine();
const aiAnalytics = new AIAnalytics();

// Create metrics with historical data
const salesMetric: KPIMetric = {
  id: 'sales-volume',
  name: 'Daily Sales Volume',
  description: 'Number of sales transactions per day',
  category: 'Sales',
  unit: 'transactions',
  currentValue: 450,
  targetValue: 500,
  threshold: {
    excellent: 500,
    good: 400,
    warning: 300,
    critical: 200
  },
  trend: {
    direction: TrendDirection.UP,
    percentage: 12.5,
    comparisonPeriod: TimePeriod.WEEKLY
  },
  historicalData: generateSampleData(60, 420, 0.08),
  status: KPIStatus.GOOD,
  tags: ['sales', 'volume', 'daily']
};

const revenueMetric: KPIMetric = {
  id: 'daily-revenue',
  name: 'Daily Revenue',
  description: 'Total revenue per day',
  category: 'Financial',
  unit: 'USD',
  currentValue: 45000,
  targetValue: 50000,
  threshold: {
    excellent: 50000,
    good: 40000,
    warning: 30000,
    critical: 20000
  },
  trend: {
    direction: TrendDirection.UP,
    percentage: 15.2,
    comparisonPeriod: TimePeriod.WEEKLY
  },
  historicalData: generateSampleData(60, 42000, 0.1),
  status: KPIStatus.GOOD,
  tags: ['revenue', 'financial', 'daily']
};

function demonstrateAIFeatures(): void {
  console.log('=== Commercial View - AI Analytics Example ===\n');

  // 1. Future Predictions
  console.log('1. PREDICTIVE ANALYTICS');
  console.log('------------------------');
  const predictions = aiAnalytics.predictFutureValues(salesMetric.historicalData, 7);
  console.log(`\nPredicting next 7 periods for ${salesMetric.name}:`);
  predictions.forEach((pred, index) => {
    const confidence = (pred.metadata?.confidence as number) * 100;
    console.log(`  Day ${index + 1}: ${formatNumber(pred.value, 0)} ${salesMetric.unit} (${formatPercentage(confidence, 0)} confidence)`);
  });

  // 2. Anomaly Detection
  console.log('\n\n2. ANOMALY DETECTION');
  console.log('---------------------');
  const anomalies = aiAnalytics.detectAnomalies(salesMetric.historicalData, 2);
  console.log(`\nDetected ${anomalies.length} anomalies in ${salesMetric.name}:`);
  anomalies.slice(0, 5).forEach(anomaly => {
    console.log(`  ${anomaly.timestamp.toISOString().split('T')[0]}: ${formatNumber(anomaly.value, 0)} ${salesMetric.unit}`);
  });

  // 3. AI Insights Generation
  console.log('\n\n3. AI-GENERATED INSIGHTS');
  console.log('-------------------------');
  const insights = aiAnalytics.generateInsights([salesMetric, revenueMetric]);
  console.log(`\nGenerated ${insights.length} insights:`);
  insights.forEach((insight, index) => {
    console.log(`  ${index + 1}. ${insight}`);
  });

  // 4. Correlation Analysis
  console.log('\n\n4. CORRELATION ANALYSIS');
  console.log('------------------------');
  const correlation = aiAnalytics.calculateCorrelation(salesMetric, revenueMetric);
  console.log(`\nCorrelation between ${salesMetric.name} and ${revenueMetric.name}:`);
  console.log(`  Correlation coefficient: ${correlation.toFixed(3)}`);
  
  if (correlation > 0.7) {
    console.log(`  ✓ Strong positive correlation - metrics move together`);
  } else if (correlation > 0.3) {
    console.log(`  ~ Moderate positive correlation`);
  } else if (correlation < -0.7) {
    console.log(`  ✗ Strong negative correlation - metrics move oppositely`);
  } else {
    console.log(`  - Weak or no correlation`);
  }

  // 5. Advanced Predictions with Confidence Intervals
  console.log('\n\n5. ADVANCED PREDICTIONS');
  console.log('------------------------');
  const revenuePredictions = aiAnalytics.predictFutureValues(revenueMetric.historicalData, 14);
  console.log(`\nTwo-week revenue forecast for ${revenueMetric.name}:`);
  
  let totalPredicted = 0;
  revenuePredictions.forEach((pred, index) => {
    totalPredicted += pred.value;
    if (index % 7 === 6) { // Every week
      const weekNum = Math.floor(index / 7) + 1;
      console.log(`  Week ${weekNum} Total: $${formatNumber(totalPredicted, 0)}`);
      totalPredicted = 0;
    }
  });

  // 6. Quality and Reliability Metrics
  console.log('\n\n6. PREDICTION QUALITY');
  console.log('----------------------');
  const avgConfidence = predictions.reduce((sum, p) => 
    sum + ((p.metadata?.confidence as number) || 0), 0) / predictions.length;
  console.log(`\nAverage prediction confidence: ${formatPercentage(avgConfidence * 100, 1)}`);
  console.log(`Data points analyzed: ${salesMetric.historicalData.length}`);
  console.log(`Prediction horizon: ${predictions.length} periods`);

  // 7. Actionable Recommendations
  console.log('\n\n7. ACTIONABLE RECOMMENDATIONS');
  console.log('-------------------------------');
  console.log('\nBased on AI analysis:');
  
  if (salesMetric.trend.percentage > 10) {
    console.log('  ✓ Sales momentum is strong - consider scaling operations');
  }
  
  if (anomalies.length > 5) {
    console.log('  ⚠ Multiple anomalies detected - investigate data quality');
  }
  
  if (correlation > 0.7) {
    console.log('  ✓ Strong correlation found - optimize joint metrics');
  }
  
  const lastPrediction = predictions[predictions.length - 1];
  const lastConfidence = lastPrediction.metadata?.confidence as number;
  if (lastConfidence < 0.7) {
    console.log('  ⚠ Long-term prediction confidence is low - gather more data');
  }

  console.log('\n');
}

// Run the AI demonstration
demonstrateAIFeatures();

export { aiAnalytics, salesMetric, revenueMetric };
