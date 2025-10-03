/**
 * AI Integration Module for Commercial View
 * Provides AI/ML capabilities for predictive analytics and insights
 */

import { KPIMetric, DataPoint, AIPredictionConfig } from '../models/types';

/**
 * AI Analytics Engine
 * Provides machine learning and predictive analytics capabilities
 */
export class AIAnalytics {
  private models: Map<string, AIPredictionConfig> = new Map();

  /**
   * Register an AI model
   */
  public registerModel(config: AIPredictionConfig): void {
    this.models.set(config.modelId, config);
  }

  /**
   * Predict future values using time series analysis
   * Simple implementation - can be extended with actual ML libraries
   */
  public predictFutureValues(
    historicalData: DataPoint[],
    periodsAhead: number
  ): DataPoint[] {
    if (historicalData.length < 2) {
      return [];
    }

    // Simple linear regression for demonstration
    const predictions: DataPoint[] = [];
    const sortedData = [...historicalData].sort((a, b) => 
      a.timestamp.getTime() - b.timestamp.getTime()
    );

    const n = sortedData.length;
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;

    sortedData.forEach((point, index) => {
      sumX += index;
      sumY += point.value;
      sumXY += index * point.value;
      sumX2 += index * index;
    });

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    const lastTimestamp = sortedData[n - 1].timestamp.getTime();
    const timeDiff = sortedData[n - 1].timestamp.getTime() - sortedData[n - 2].timestamp.getTime();

    for (let i = 1; i <= periodsAhead; i++) {
      const predictedValue = slope * (n + i - 1) + intercept;
      predictions.push({
        timestamp: new Date(lastTimestamp + timeDiff * i),
        value: Math.max(0, predictedValue), // Ensure non-negative
        metadata: {
          predicted: true,
          confidence: this.calculateConfidence(sortedData, i)
        }
      });
    }

    return predictions;
  }

  /**
   * Calculate prediction confidence
   */
  private calculateConfidence(_data: DataPoint[], periodsAhead: number): number {
    // Confidence decreases with distance from known data
    const baseConfidence = 0.95;
    const decayFactor = 0.05;
    return Math.max(0.5, baseConfidence - (periodsAhead * decayFactor));
  }

  /**
   * Detect anomalies in KPI data
   */
  public detectAnomalies(data: DataPoint[], threshold: number = 2): DataPoint[] {
    if (data.length < 3) {
      return [];
    }

    const values = data.map(d => d.value);
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    // If standard deviation is zero, all values are identical (no variance),
    // so anomaly detection is meaningless; return empty array.
    if (stdDev === 0) {
      return [];
    }

    // Filter and return data points that are more than `threshold` standard deviations from the mean
    return data.filter(d => Math.abs((d.value - mean) / stdDev) > threshold);
  }

  /**
   * Generate AI-powered insights from metrics
   */
  public generateInsights(metrics: KPIMetric[]): string[] {
    const insights: string[] = [];

    metrics.forEach(metric => {
      // Analyze trends
      if (metric.trend.percentage > 10) {
        insights.push(
          `${metric.name} shows strong positive growth of ${metric.trend.percentage.toFixed(1)}% - consider capitalizing on this trend`
        );
      } else if (metric.trend.percentage < -10) {
        insights.push(
          `${metric.name} declining by ${Math.abs(metric.trend.percentage).toFixed(1)}% - immediate attention required`
        );
      }

      // Analyze against targets
      if (metric.targetValue && metric.currentValue >= metric.targetValue * 1.1) {
        insights.push(
          `${metric.name} exceeding target by ${((metric.currentValue / metric.targetValue - 1) * 100).toFixed(1)}% - exceptional performance`
        );
      } else if (metric.targetValue && metric.currentValue < metric.targetValue * 0.8) {
        insights.push(
          `${metric.name} at ${((metric.currentValue / metric.targetValue) * 100).toFixed(1)}% of target - requires intervention`
        );
      }

      // Detect anomalies
      const anomalies = this.detectAnomalies(metric.historicalData);
      if (anomalies.length > 0) {
        insights.push(
          `${metric.name} has ${anomalies.length} anomalous data points detected - review data quality`
        );
      }
    });

    return insights;
  }

  /**
   * Calculate correlation between two metrics
   */
  public calculateCorrelation(metric1: KPIMetric, metric2: KPIMetric): number {
    const data1 = metric1.historicalData.map(d => d.value);
    const data2 = metric2.historicalData.map(d => d.value);

    if (data1.length !== data2.length || data1.length === 0) {
      return 0;
    }

    const n = data1.length;
    const mean1 = data1.reduce((a, b) => a + b, 0) / n;
    const mean2 = data2.reduce((a, b) => a + b, 0) / n;

    let numerator = 0;
    let sum1Sq = 0;
    let sum2Sq = 0;

    for (let i = 0; i < n; i++) {
      const diff1 = data1[i] - mean1;
      const diff2 = data2[i] - mean2;
      numerator += diff1 * diff2;
      sum1Sq += diff1 * diff1;
      sum2Sq += diff2 * diff2;
    }

    const denominator = Math.sqrt(sum1Sq * sum2Sq);
    return denominator === 0 ? 0 : numerator / denominator;
  }
}
