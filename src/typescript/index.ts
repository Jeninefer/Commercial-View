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

export interface LoanData {
  loanId: string;
  borrowerName: string;
  principalAmount: number;
  interestRate: number;
  termMonths: number;
  remainingBalance: number;
  nextPaymentDate: string;
  status: 'active' | 'delinquent' | 'paid_off' | 'charged_off';
}

export interface PaymentSchedule {
  paymentId: string;
  loanId: string;
  dueDate: string;
  principalAmount: number;
  interestAmount: number;
  totalAmount: number;
  status: 'pending' | 'paid' | 'overdue';
}

export interface CollateralData {
  collateralId: string;
  loanId: string;
  type: string;
  description: string;
  estimatedValue: number;
  lastAppraisalDate: string;
}

export interface CustomerData {
  customerId: string;
  name: string;
  creditScore: number;
  totalExposure: number;
  riskRating: 'low' | 'medium' | 'high';
  lastReviewDate: string;
}

export class CommercialViewClient {
  private baseUrl: string;
  private headers: HeadersInit;

  constructor(baseUrl: string = 'http://localhost:8000', apiKey?: string) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Content-Type': 'application/json',
      ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
    };
  }

  private async makeRequest<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: this.headers
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        data,
        status: 'success'
      };
    } catch (error) {
      return {
        data: null as T,
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async getExecutiveSummary(): Promise<ApiResponse<ExecutiveSummary>> {
    return this.makeRequest<ExecutiveSummary>('/executive-summary');
  }

  async getHealth(): Promise<ApiResponse<{ status: string }>> {
    return this.makeRequest<{ status: string }>('/health');
  }

  async getLoanData(): Promise<ApiResponse<LoanData[]>> {
    return this.makeRequest<LoanData[]>('/loan-data');
  }

  async getPaymentSchedule(): Promise<ApiResponse<PaymentSchedule[]>> {
    return this.makeRequest<PaymentSchedule[]>('/payment-schedule');
  }

  async getCollateralData(): Promise<ApiResponse<CollateralData[]>> {
    return this.makeRequest<CollateralData[]>('/collateral-data');
  }

  async getCustomerData(): Promise<ApiResponse<CustomerData[]>> {
    return this.makeRequest<CustomerData[]>('/customer-data');
  }

  async getPortfolioMetrics(): Promise<ApiResponse<PortfolioOverview>> {
    return this.makeRequest<PortfolioOverview>('/portfolio-metrics');
  }

  async getHistoricPayments(): Promise<ApiResponse<PaymentSchedule[]>> {
    return this.makeRequest<PaymentSchedule[]>('/historic-payments');
  }

  async getSchema(): Promise<ApiResponse<Record<string, any>>> {
    return this.makeRequest<Record<string, any>>('/schema');
  }

  // Utility method to test connection
  async testConnection(): Promise<boolean> {
    const healthCheck = await this.getHealth();
    return healthCheck.status === 'success';
  }

  // Method to get API base URL
  getBaseUrl(): string {
    return this.baseUrl;
  }

  // Method to update headers (e.g., for authentication)
  updateHeaders(newHeaders: HeadersInit): void {
    this.headers = { ...this.headers, ...newHeaders };
  }
}

export default CommercialViewClient;
