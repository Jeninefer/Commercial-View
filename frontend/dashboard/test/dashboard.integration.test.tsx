import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../src/App';
import { DashboardStoreProvider } from '../src/state/dashboardStore';
import * as dashboardApi from '../src/api/dashboard';
import {
  ExecutiveSummaryResponse,
  PortfolioTrendResponse,
  RiskExposureResponse,
  CsvIngestionResponse,
} from '../src/types';

vi.mock('../src/api/dashboard');

const mockedDashboardApi = vi.mocked(dashboardApi, true);

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
    },
  });

describe('Commercial-View dashboard', () => {
  const executiveSummary: ExecutiveSummaryResponse = {
    data: {
      metrics: [
        {
          id: 'total-outstanding',
          label: 'Total Outstanding',
          value: 120_000_000,
          change: 0.02,
          changeLabel: '+2.0% vs. last month',
          status: 'onTrack',
          unit: 'currency',
          target: 125_000_000,
        },
        {
          id: 'risk-score',
          label: 'Average Risk Score',
          value: 3.4,
          change: -0.1,
          changeLabel: '-10 bps vs. plan',
          status: 'atRisk',
          unit: 'ratio',
        },
      ],
      insights: ['Portfolio growth above target with stable risk profile.'],
    },
    meta: { lastUpdated: '2024-05-01T12:00:00Z', source: 'api' },
  };

  const trendResponse: PortfolioTrendResponse = {
    data: [
      {
        metricId: 'originations',
        label: 'Originations',
        unit: 'currency',
        points: [
          { period: 'Jan', actual: 12_000_000, target: 11_000_000 },
          { period: 'Feb', actual: 13_500_000, target: 12_000_000 },
          { period: 'Mar', actual: 15_200_000, target: 14_000_000 },
        ],
      },
    ],
    meta: { lastUpdated: '2024-05-01T12:00:00Z', source: 'api' },
  };

  const riskResponse: RiskExposureResponse = {
    data: {
      riskDistribution: [
        {
          segment: 'Middle Market',
          outstanding: 65_000_000,
          delinquencyRate: 0.012,
          lossGivenDefault: 0.32,
          riskLevel: 'Moderate',
        },
        {
          segment: 'CRE',
          outstanding: 48_000_000,
          delinquencyRate: 0.021,
          lossGivenDefault: 0.41,
          riskLevel: 'Elevated',
        },
      ],
      topExposures: [
        {
          borrower: 'Atlas Manufacturing',
          relationshipManager: 'Jordan Chen',
          outstanding: 18_500_000,
          riskScore: 3.9,
          industry: 'Industrial',
          nextReview: '2024-07-15',
        },
        {
          borrower: 'Sequoia Hospitality Group',
          relationshipManager: 'Priya Patel',
          outstanding: 22_000_000,
          riskScore: 4.4,
          industry: 'Hospitality',
          nextReview: '2024-08-01',
        },
      ],
    },
    meta: { lastUpdated: '2024-05-01T12:00:00Z', source: 'api' },
  };

  const ingestionResponse: CsvIngestionResponse = {
    ingestedRows: 250,
    preview: [
      { Borrower: 'Atlas Manufacturing', Exposure: 18500000, 'Risk Score': 3.9 },
      { Borrower: 'Sequoia Hospitality Group', Exposure: 22000000, 'Risk Score': 4.4 },
    ],
    lastUpdated: '2024-05-02T08:00:00Z',
  };

  const renderDashboard = () => {
    const queryClient = createQueryClient();

    return render(
      <QueryClientProvider client={queryClient}>
        <DashboardStoreProvider>
          <App />
        </DashboardStoreProvider>
      </QueryClientProvider>,
    );
  };

  beforeEach(() => {
    vi.resetAllMocks();
    mockedDashboardApi.fetchExecutiveSummary.mockResolvedValue(executiveSummary);
    mockedDashboardApi.fetchPortfolioTrends.mockResolvedValue(trendResponse);
    mockedDashboardApi.fetchRiskExposure.mockResolvedValue(riskResponse);
    mockedDashboardApi.uploadPortfolioCsv.mockResolvedValue(ingestionResponse);
  });

  it('renders KPI tiles, charts, tables, and processes CSV ingestion', async () => {
    renderDashboard();

    expect(await screen.findByText('Total Outstanding')).toBeInTheDocument();
    expect(screen.getByText('$120,000,000')).toBeInTheDocument();

    expect(await screen.findByRole('figure', { name: /portfolio trend performance/i })).toBeInTheDocument();
    expect(screen.getByRole('table', { name: /risk distribution/i })).toBeInTheDocument();
    expect(screen.getByRole('table', { name: /top portfolio exposures/i })).toBeInTheDocument();

    const uploadInput = screen.getByLabelText(/upload csv/i);
    const file = new File(['Borrower,Exposure\n'], 'portfolio.csv', { type: 'text/csv' });
    fireEvent.change(uploadInput, { target: { files: [file] } });

    await waitFor(() =>
      expect(screen.getByText(/Ingested/)).toHaveTextContent('Ingested 250 rows'),
    );
  });

  it('surfaces API errors for KPI tiles and CSV uploads', async () => {
    mockedDashboardApi.fetchExecutiveSummary.mockRejectedValue({
      response: { data: { message: 'Service unavailable' }, status: 503 },
    });
    mockedDashboardApi.uploadPortfolioCsv.mockRejectedValue({
      response: { data: { message: 'Validation failed' }, status: 400 },
    });

    renderDashboard();

    expect(
      await screen.findByText(/We couldn't load KPI metrics/i, undefined, {
        timeout: 4000,
      }),
    ).toBeInTheDocument();

    const uploadInput = screen.getByLabelText(/upload csv/i);
    const file = new File(['Borrower,Exposure\n'], 'portfolio.csv', { type: 'text/csv' });
    fireEvent.change(uploadInput, { target: { files: [file] } });

    await waitFor(() =>
      expect(screen.getByText(/Upload failed/i)).toBeInTheDocument(),
    );
  });
});
