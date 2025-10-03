/**
 * Utility Functions for Commercial View
 * Helper functions for data processing and analysis
 */

import { DataPoint, TimePeriod } from '../models/types';

/**
 * Format numbers with proper thousand separators
 */
export function formatNumber(value: number, decimals: number = 2): string {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

/**
 * Format currency values
 */
export function formatCurrency(value: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(value);
}

/**
 * Format percentage values
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Calculate average from data points
 */
export function calculateAverage(data: DataPoint[]): number {
  if (data.length === 0) return 0;
  const sum = data.reduce((acc, point) => acc + point.value, 0);
  return sum / data.length;
}

/**
 * Calculate median from data points
 */
export function calculateMedian(data: DataPoint[]): number {
  if (data.length === 0) return 0;
  
  const sorted = [...data].sort((a, b) => a.value - b.value);
  const mid = Math.floor(sorted.length / 2);
  
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1].value + sorted[mid].value) / 2;
  }
  return sorted[mid].value;
}

/**
 * Calculate standard deviation
 */
export function calculateStandardDeviation(data: DataPoint[]): number {
  if (data.length === 0) return 0;
  
  const avg = calculateAverage(data);
  const squareDiffs = data.map(point => Math.pow(point.value - avg, 2));
  const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / squareDiffs.length;
  
  return Math.sqrt(avgSquareDiff);
}

/**
 * Filter data points by time period
 */
export function filterByTimePeriod(data: DataPoint[], period: TimePeriod): DataPoint[] {
  const now = new Date();
  const cutoffDate = new Date(now);

  switch (period) {
    case TimePeriod.HOURLY:
      cutoffDate.setHours(now.getHours() - 1);
      break;
    case TimePeriod.DAILY:
      cutoffDate.setDate(now.getDate() - 1);
      break;
    case TimePeriod.WEEKLY:
      cutoffDate.setDate(now.getDate() - 7);
      break;
    case TimePeriod.MONTHLY:
      cutoffDate.setMonth(now.getMonth() - 1);
      break;
    case TimePeriod.QUARTERLY:
      cutoffDate.setMonth(now.getMonth() - 3);
      break;
    case TimePeriod.YEARLY:
      cutoffDate.setFullYear(now.getFullYear() - 1);
      break;
    default:
      return data;
  }

  return data.filter(point => point.timestamp >= cutoffDate);
}

/**
 * Group data points by time period
 */
export function groupByTimePeriod(
  data: DataPoint[],
  period: TimePeriod
): Map<string, DataPoint[]> {
  const grouped = new Map<string, DataPoint[]>();

  data.forEach(point => {
    let key: string;
    const date = point.timestamp;

    switch (period) {
      case TimePeriod.HOURLY:
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
        break;
      case TimePeriod.DAILY:
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
        break;
      case TimePeriod.WEEKLY: {
        const weekNumber = Math.floor(date.getDate() / 7);
        key = `${date.getFullYear()}-${date.getMonth()}-W${weekNumber}`;
        break;
      }
      case TimePeriod.MONTHLY:
        key = `${date.getFullYear()}-${date.getMonth()}`;
        break;
      case TimePeriod.QUARTERLY: {
        const quarter = Math.floor(date.getMonth() / 3) + 1;
        key = `${date.getFullYear()}-Q${quarter}`;
        break;
      }
      case TimePeriod.YEARLY:
        key = `${date.getFullYear()}`;
        break;
      default:
        key = date.toISOString();
    }

    if (!grouped.has(key)) {
      grouped.set(key, []);
    }
    grouped.get(key)?.push(point);
  });

  return grouped;
}

/**
 * Validate data quality
 */
export function validateDataQuality(data: DataPoint[]): {
  isValid: boolean;
  issues: string[];
} {
  const issues: string[] = [];

  if (data.length === 0) {
    issues.push('No data points available');
  }

  const nullValues = data.filter(p => p.value === null || p.value === undefined);
  if (nullValues.length > 0) {
    issues.push(`${nullValues.length} null values found`);
  }

  const duplicateTimestamps = new Set(data.map(p => p.timestamp.getTime())).size !== data.length;
  if (duplicateTimestamps) {
    issues.push('Duplicate timestamps detected');
  }

  return {
    isValid: issues.length === 0,
    issues
  };
}

/**
 * Generate sample data for testing
 */
export function generateSampleData(
  count: number,
  baseValue: number = 100,
  volatility: number = 0.1
): DataPoint[] {
  const data: DataPoint[] = [];
  let currentValue = baseValue;
  const now = Date.now();

  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 2 * volatility * baseValue;
    currentValue += change;

    data.push({
      timestamp: new Date(now - (count - i) * 3600000), // Hourly data
      value: Math.max(0, currentValue),
      metadata: {
        generated: true
      }
    });
  }

  return data;
}
