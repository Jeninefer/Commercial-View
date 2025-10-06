import client from './client';
import {
  ExecutiveSummaryResponse,
  PortfolioTrendResponse,
  RiskExposureResponse,
  CsvIngestionPayload,
  CsvIngestionResponse,
} from '../types/api';

export const fetchExecutiveSummary = async (): Promise<ExecutiveSummaryResponse> => {
  const { data } = await client.get<ExecutiveSummaryResponse>('/executive-summary');
  return data;
};

export const fetchPortfolioTrends = async (): Promise<PortfolioTrendResponse> => {
  const { data } = await client.get<PortfolioTrendResponse>('/portfolio/trends');
  return data;
};

export const fetchRiskExposure = async (): Promise<RiskExposureResponse> => {
  const { data } = await client.get<RiskExposureResponse>('/portfolio/risk-exposure');
  return data;
};

export const uploadPortfolioCsv = async (
  payload: CsvIngestionPayload,
): Promise<CsvIngestionResponse> => {
  const body = new FormData();
  body.append('file', payload.file);
  if (payload.replaceExisting) {
    body.append('replace', 'true');
  }

  const { data } = await client.post<CsvIngestionResponse>('/portfolio/ingest', body, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};
