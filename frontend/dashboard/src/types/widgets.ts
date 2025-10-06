import { KpiMetric, PortfolioTrendSeries, RiskDistributionRow, ExposureRow } from './dashboard';
import { CsvIngestionState } from './state';

export interface WidgetBaseProps {
  loading?: boolean;
  error?: string;
}

export interface KpiGridProps extends WidgetBaseProps {
  metrics: KpiMetric[];
}

export interface TrendChartProps extends WidgetBaseProps {
  series: PortfolioTrendSeries[];
}

export interface RiskDistributionTableProps extends WidgetBaseProps {
  rows: RiskDistributionRow[];
}

export interface ExposureTableProps extends WidgetBaseProps {
  rows: ExposureRow[];
}

export interface CsvUploaderProps {
  onUpload: (file: File, replaceExisting?: boolean) => Promise<void> | void;
  onDismissError: () => void;
  state: CsvIngestionState;
}
