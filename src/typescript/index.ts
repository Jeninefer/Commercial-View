/**
 * Commercial-View TypeScript utilities
 * Provides type definitions and utilities for the project
 */

export interface PortfolioOverview {
  totalAccounts: number;
  totalBalance: number;
  averageRiskScore: number;
  performanceMetrics: {
    currentMonth: number;
    previousMonth: number;
    yearToDate: number;
  };
}

export interface RiskIndicators {
  defaultRate: number;
  concentrationRisk: number;
  liquidityRisk: number;
  creditRisk: number;
}

export interface ExecutiveSummary {
  portfolioOverview: PortfolioOverview;
  riskIndicators: RiskIndicators;
  timestamp: string;
}

export interface ApiResponse<T = any> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export class CommercialViewClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getExecutiveSummary(): Promise<ApiResponse<ExecutiveSummary>> {
    try {
      const response = await fetch(`${this.baseUrl}/executive-summary`);
      const data = await response.json();
      
      return {
        data,
        status: 'success'
      };
    } catch (error) {
      return {
        data: null,
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async getHealth(): Promise<ApiResponse<{ status: string }>> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      const data = await response.json();
      
      return {
        data,
        status: 'success'
      };
    } catch (error) {
      return {
        data: null,
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}

export default CommercialViewClient;
