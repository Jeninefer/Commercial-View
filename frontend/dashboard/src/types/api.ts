import { ExecutiveSummary, PortfolioTrendSeries, RiskExposure } from './dashboard';

export interface ApiMeta {
  lastUpdated: string;
  source: string;
}

export interface ApiResponse<T> {
  data: T;
  meta: ApiMeta;
}

export interface ApiError {
  message: string;
  statusCode?: number;
}

export type ExecutiveSummaryResponse = ApiResponse<ExecutiveSummary>;

export type PortfolioTrendResponse = ApiResponse<PortfolioTrendSeries[]>;

export type RiskExposureResponse = ApiResponse<RiskExposure>;

export interface CsvPreviewRow {
  [key: string]: string | number | null;
}

export interface CsvIngestionResponse {
  ingestedRows: number;
  preview: CsvPreviewRow[];
  lastUpdated: string;
}

export interface CsvIngestionPayload {
  file: File;
  replaceExisting?: boolean;
}
