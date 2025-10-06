import { MetricUnit } from '../types/dashboard';

const CURRENCY_FORMATTER = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const PERCENTAGE_FORMATTER = new Intl.NumberFormat('en-US', {
  style: 'percent',
  maximumFractionDigits: 1,
});

const NUMBER_FORMATTER = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 0,
});

export const formatMetricValue = (value: number, unit: MetricUnit): string => {
  switch (unit) {
    case 'currency':
      return CURRENCY_FORMATTER.format(value);
    case 'percentage':
      return PERCENTAGE_FORMATTER.format(value);
    case 'ratio':
      return value.toFixed(2);
    case 'count':
    default:
      return NUMBER_FORMATTER.format(value);
  }
};

export const formatChange = (change: number, unit: MetricUnit): string => {
  if (unit === 'percentage' || unit === 'ratio') {
    return `${change >= 0 ? '+' : ''}${(change * 100).toFixed(1)}bps`;
  }

  if (unit === 'currency') {
    return `${change >= 0 ? '+' : ''}${NUMBER_FORMATTER.format(change)} ${change >= 0 ? '↑' : '↓'}`;
  }

  return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
};
