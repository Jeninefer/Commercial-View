/**
 * Commercial-View TypeScript utilities
 * Provides comprehensive type definitions and utilities for commercial lending platform
 */

// Core Portfolio and Risk Types
export interface PortfolioOverview {
  totalAccounts: number;
  totalBalance: number;
  averageRiskScore: number;
  performanceMetrics: {
    currentMonth: number;
    previousMonth: number;
    yearToDate: number;
    quarterToDate?: number;
  };
  concentration: {
    byIndustry: Record<string, number>;
    byGeography: Record<string, number>;
    byLoanSize: Record<string, number>;
  };
}

export interface RiskIndicators {
  defaultRate: number;
  concentrationRisk: number;
  liquidityRisk: number;
  creditRisk: number;
  operationalRisk?: number;
  marketRisk?: number;
  regulatoryRisk?: number;
}

export interface ExecutiveSummary {
  portfolioOverview: PortfolioOverview;
  riskIndicators: RiskIndicators;
  timestamp: string;
  generatedBy?: string;
  reportPeriod: {
    startDate: string;
    endDate: string;
  };
}

// Enhanced Commercial Lending Types
export interface CommercialLoanData extends LoanData {
  businessType: 'real_estate' | 'equipment' | 'working_capital' | 'term_loan' | 'line_of_credit';
  industryCode: string;
  industryName: string;
  guarantorInfo?: GuarantorData[];
  covenants?: LoanCovenant[];
  lastReviewDate: string;
  nextReviewDate: string;
  loanToValueRatio?: number;
  debtServiceCoverageRatio?: number;
}

export interface GuarantorData {
  guarantorId: string;
  name: string;
  guaranteeAmount: number;
  guaranteeType: 'personal' | 'corporate' | 'limited';
  creditScore?: number;
  netWorth?: number;
}

export interface LoanCovenant {
  covenantId: string;
  type: 'financial' | 'operational' | 'reporting';
  description: string;
  threshold: number;
  currentValue?: number;
  complianceStatus: 'compliant' | 'breach' | 'watch';
  lastTestDate: string;
}

// Days Past Due (DPD) Analysis Types
export interface DPDAnalysis {
  loanId: string;
  currentDPD: number;
  dpdCategory: '0-30' | '31-60' | '61-90' | '91-120' | '120+';
  dpdTrend: 'improving' | 'stable' | 'deteriorating';
  historicalDPD: DPDHistoryPoint[];
  projectedDPD?: number;
  actionRequired: boolean;
  recommendedActions?: string[];
}

export interface DPDHistoryPoint {
  date: string;
  dpd: number;
  paymentAmount?: number;
}

// KPI and Performance Types
export interface KPIMetrics {
  portfolioKPIs: {
    totalCommitments: number;
    totalOutstandings: number;
    utilizationRate: number;
    weightedAverageRate: number;
    averageMaturity: number;
  };
  riskKPIs: {
    probabilityOfDefault: number;
    lossGivenDefault: number;
    exposureAtDefault: number;
    expectedLoss: number;
  };
  profitabilityKPIs: {
    netInterestMargin: number;
    returnOnAssets: number;
    returnOnEquity: number;
    costOfFunds: number;
  };
  operationalKPIs: {
    avgLoanProcessingTime: number;
    loanApprovalRate: number;
    customerSatisfactionScore?: number;
  };
}

// Pricing and Rate Management Types
export interface PricingMatrix {
  loanType: string;
  riskGrade: string;
  termBand: string;
  baseRate: number;
  riskAdjustment: number;
  finalRate: number;
  effectiveDate: string;
  expiryDate?: string;
}

export interface RateAdjustment {
  adjustmentId: string;
  loanId: string;
  currentRate: number;
  proposedRate: number;
  reason: string;
  effectiveDate: string;
  approvalStatus: 'pending' | 'approved' | 'rejected';
  approvedBy?: string;
}

// Enhanced API Response Types
export interface ApiResponse<T = any> {
  data: T;
  status: 'success' | 'error';
  message?: string;
  metadata?: {
    timestamp: string;
    version: string;
    requestId?: string;
    executionTime?: number;
  };
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    totalPages: number;
    totalRecords: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
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

// Enhanced Commercial-View Client
export class CommercialViewClient {
  private baseUrl: string;
  private headers: HeadersInit;
  private config: Partial<CommercialViewConfig>;

  constructor(
    baseUrl: string = 'http://localhost:8000', 
    apiKey?: string,
    config?: Partial<CommercialViewConfig>
  ) {
    this.baseUrl = baseUrl;
    this.config = {
      timeout: 30000,
      retryAttempts: 3,
      enableCache: false,
      ...config
    };
    
    this.headers = {
      'Content-Type': 'application/json',
      'X-Client-Version': '1.0.0',
      ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
    };
  }

  private async makeRequest<T>(
    endpoint: string, 
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    const startTime = Date.now();
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout || 30000);

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: this.headers,
        signal: controller.signal,
        ...options
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const executionTime = Date.now() - startTime;
      
      return {
        data,
        status: 'success',
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
          executionTime
        }
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      
      return {
        data: null as T,
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error',
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
          executionTime
        }
      };
    }
  }

  // Enhanced API Methods
  async getHealth(): Promise<ApiResponse<{ status: string; timestamp: string; version: string }>> {
    return this.makeRequest<{ status: string; timestamp: string; version: string }>('/health');
  }

  async getExecutiveSummary(dateRange?: { startDate: string; endDate: string }): Promise<ApiResponse<ExecutiveSummary>> {
    const params = dateRange ? `?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}` : '';
    return this.makeRequest<ExecutiveSummary>(`/api/v1/executive-summary${params}`);
  }

  async getCommercialLoans(filters?: Record<string, any>): Promise<ApiResponse<CommercialLoanData[]>> {
    const params = filters ? `?${new URLSearchParams(filters).toString()}` : '';
    return this.makeRequest<CommercialLoanData[]>(`/api/v1/commercial-loans${params}`);
  }

  // Legacy support methods
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

  // Enhanced commercial lending methods
  async getDPDAnalysis(loanId?: string): Promise<ApiResponse<DPDAnalysis[]>> {
    const endpoint = loanId ? `/api/v1/dpd-analysis/${loanId}` : '/api/v1/dpd-analysis';
    return this.makeRequest<DPDAnalysis[]>(endpoint);
  }

  async getKPIMetrics(period?: string): Promise<ApiResponse<KPIMetrics>> {
    const params = period ? `?period=${period}` : '';
    return this.makeRequest<KPIMetrics>(`/api/v1/kpi-metrics${params}`);
  }

  async getPricingMatrix(): Promise<ApiResponse<PricingMatrix[]>> {
    return this.makeRequest<PricingMatrix[]>('/api/v1/pricing-matrix');
  }

  async getRiskAssessment(loanId: string): Promise<ApiResponse<RiskAssessmentResult>> {
    return this.makeRequest<RiskAssessmentResult>(`/api/v1/risk-assessment/${loanId}`);
  }

  async getPortfolioAnalysis(filters?: Record<string, any>): Promise<ApiResponse<PortfolioAnalysisResult>> {
    const params = filters ? `?${new URLSearchParams(filters).toString()}` : '';
    return this.makeRequest<PortfolioAnalysisResult>(`/api/v1/portfolio-analysis${params}`);
  }

  async getStressTest(scenario: StressTestScenario): Promise<ApiResponse<StressTestResult>> {
    return this.makeRequest<StressTestResult>('/api/v1/stress-test', {
      method: 'POST',
      body: JSON.stringify(scenario)
    });
  }

  async generateReport(request: ReportRequest): Promise<ApiResponse<ExportResult>> {
    return this.makeRequest<ExportResult>('/api/v1/reports/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async getReportStatus(exportId: string): Promise<ApiResponse<ExportResult>> {
    return this.makeRequest<ExportResult>(`/api/v1/reports/status/${exportId}`);
  }

  // Pagination support
  async getPaginatedLoans(
    page: number = 1,
    pageSize: number = 50,
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<CommercialLoanData>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...filters
    });
    
    return this.makeRequest<CommercialLoanData[]>(`/api/v1/commercial-loans/paginated?${params}`);
  }

  // Batch operations
  async batchUpdateRates(updates: RateAdjustment[]): Promise<ApiResponse<{ updated: number; failed: number }>> {
    return this.makeRequest('/api/v1/rates/batch-update', {
      method: 'POST',
      body: JSON.stringify({ updates })
    });
  }

  // Utility method to test connection
  async testConnection(): Promise<{ connected: boolean; details: Record<string, any> }> {
    const healthCheck = await this.getHealth();
    const connected = healthCheck.status === 'success';
    
    return {
      connected,
      details: {
        baseUrl: this.baseUrl,
        responseTime: healthCheck.metadata?.executionTime,
        timestamp: healthCheck.metadata?.timestamp,
        version: healthCheck.metadata?.version
      }
    };
  }

  // Configuration management
  updateConfig(newConfig: Partial<CommercialViewConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  getConfig(): Partial<CommercialViewConfig> {
    return { ...this.config };
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

// Configuration and Settings Types
export interface CommercialViewConfig {
  apiBaseUrl: string;
  apiVersion: string;
  timeout: number;
  retryAttempts: number;
  enableCache: boolean;
  cacheTimeout: number;
  authentication: {
    type: 'bearer' | 'api_key' | 'oauth';
    credentials?: Record<string, string>;
  };
}

// Reporting and Export Types
export interface ReportRequest {
  reportType: 'executive_summary' | 'portfolio_analysis' | 'risk_assessment' | 'kpi_dashboard';
  parameters: {
    dateRange: {
      startDate: string;
      endDate: string;
    };
    filters?: Record<string, any>;
    format: 'json' | 'csv' | 'excel' | 'pdf';
  };
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    deliveryMethod: 'email' | 'api' | 'file_export';
    recipients?: string[];
  };
}

export interface ExportResult {
  exportId: string;
  status: 'pending' | 'completed' | 'failed';
  downloadUrl?: string;
  expiryDate?: string;
  fileSize?: number;
  recordCount?: number;
}

// Additional Commercial Lending Types
export interface RiskAssessmentResult {
  loanId: string;
  overallRiskScore: number;
  riskGrade: 'A' | 'B' | 'C' | 'D' | 'E';
  riskFactors: {
    creditRisk: number;
    concentrationRisk: number;
    industryRisk: number;
    geographicRisk: number;
    collateralRisk: number;
  };
  recommendations: string[];
  lastAssessmentDate: string;
  nextReviewDate: string;
}

export interface PortfolioAnalysisResult {
  summary: {
    totalPortfolioValue: number;
    numberOfLoans: number;
    averageLoanSize: number;
    portfolioYield: number;
  };
  concentrationAnalysis: {
    byIndustry: ConcentrationMetric[];
    byGeography: ConcentrationMetric[];
    byLoanSize: ConcentrationMetric[];
    byRiskGrade: ConcentrationMetric[];
  };
  performanceMetrics: {
    chargeOffRate: number;
    recoveryRate: number;
    netChargeOffRate: number;
    provisionCoverage: number;
  };
  trendAnalysis: {
    growthRate: number;
    yieldTrend: TrendPoint[];
    qualityTrend: TrendPoint[];
  };
}

export interface ConcentrationMetric {
  category: string;
  amount: number;
  percentage: number;
  count: number;
  riskScore: number;
}

export interface TrendPoint {
  date: string;
  value: number;
  changeFromPrevious?: number;
}

export interface StressTestScenario {
  scenarioName: string;
  description: string;
  parameters: {
    economicShock: {
      gdpDecline?: number;
      unemploymentIncrease?: number;
      interestRateChange?: number;
    };
    industryShocks?: Array<{
      industryCode: string;
      impactMultiplier: number;
    }>;
    collateralValueDecline?: number;
  };
  timeHorizon: number; // months
}

export interface StressTestResult {
  scenarioName: string;
  executionDate: string;
  results: {
    baselineMetrics: {
      expectedLoss: number;
      probabilityOfDefault: number;
      lossGivenDefault: number;
    };
    stressedMetrics: {
      expectedLoss: number;
      probabilityOfDefault: number;
      lossGivenDefault: number;
    };
    impact: {
      additionalLoss: number;
      capitalImpact: number;
      loansAtRisk: number;
    };
  };
  loanLevelResults: Array<{
    loanId: string;
    baselinePD: number;
    stressedPD: number;
    expectedLoss: number;
    riskGradeChange?: string;
  }>;
}

// Enhanced Regulatory and Compliance Types
export interface RegulatoryReport {
  reportId: string;
  reportType: 'call_report' | 'shared_national_credit' | 'stress_test' | 'concentration';
  reportingPeriod: {
    startDate: string;
    endDate: string;
  };
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  submissionDeadline: string;
  data: Record<string, any>;
  validationResults?: ValidationResult[];
}

export interface ValidationResult {
  field: string;
  rule: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  value?: any;
}

export interface ComplianceMetrics {
  legalLendingLimit: {
    singleBorrowerLimit: number;
    currentExposure: number;
    utilizationPercentage: number;
    violations: LendingLimitViolation[];
  };
  concentrationLimits: {
    industryLimits: ConcentrationLimit[];
    geographicLimits: ConcentrationLimit[];
  };
  capitalAdequacy: {
    tier1Ratio: number;
    totalCapitalRatio: number;
    leverageRatio: number;
    riskWeightedAssets: number;
  };
}

export interface LendingLimitViolation {
  borrowerId: string;
  borrowerName: string;
  currentExposure: number;
  limit: number;
  excessAmount: number;
  violationDate: string;
}

export interface ConcentrationLimit {
  category: string;
  limit: number;
  currentExposure: number;
  utilizationPercentage: number;
  status: 'compliant' | 'warning' | 'violation';
}

// Enhanced Client Methods for Regulatory Functions
export class CommercialViewClient {
  // ...existing code...

  // Regulatory and compliance methods
  async getRegulatoryReport(reportId: string): Promise<ApiResponse<RegulatoryReport>> {
    return this.makeRequest<RegulatoryReport>(`/api/v1/regulatory/reports/${reportId}`);
  }

  async generateRegulatoryReport(request: {
    reportType: string;
    reportingPeriod: { startDate: string; endDate: string };
    parameters?: Record<string, any>;
  }): Promise<ApiResponse<RegulatoryReport>> {
    return this.makeRequest<RegulatoryReport>('/api/v1/regulatory/reports/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  async getComplianceMetrics(): Promise<ApiResponse<ComplianceMetrics>> {
    return this.makeRequest<ComplianceMetrics>('/api/v1/compliance/metrics');
  }

  async validateLendingLimits(borrowerId?: string): Promise<ApiResponse<LendingLimitViolation[]>> {
    const endpoint = borrowerId 
      ? `/api/v1/compliance/lending-limits/${borrowerId}` 
      : '/api/v1/compliance/lending-limits';
    return this.makeRequest<LendingLimitViolation[]>(endpoint);
  }

  // Enhanced analytics methods
  async getConcentrationAnalysis(type: 'industry' | 'geography' | 'loan_size'): Promise<ApiResponse<ConcentrationMetric[]>> {
    return this.makeRequest<ConcentrationMetric[]>(`/api/v1/analytics/concentration/${type}`);
  }

  async getTrendAnalysis(metric: string, period: string): Promise<ApiResponse<TrendPoint[]>> {
    return this.makeRequest<TrendPoint[]>(`/api/v1/analytics/trends/${metric}?period=${period}`);
  }

  // Workflow and approval methods
  async submitForApproval(workflowType: string, itemId: string, approvers: string[]): Promise<ApiResponse<WorkflowResult>> {
    return this.makeRequest<WorkflowResult>('/api/v1/workflow/submit', {
      method: 'POST',
      body: JSON.stringify({ workflowType, itemId, approvers })
    });
  }

  async getWorkflowStatus(workflowId: string): Promise<ApiResponse<WorkflowStatus>> {
    return this.makeRequest<WorkflowStatus>(`/api/v1/workflow/status/${workflowId}`);
  }

  // ...existing code...
}

// Workflow Types
export interface WorkflowResult {
  workflowId: string;
  status: 'submitted' | 'in_progress' | 'approved' | 'rejected';
  submittedDate: string;
  approvers: WorkflowApprover[];
}

export interface WorkflowStatus {
  workflowId: string;
  currentStatus: string;
  currentApprover?: string;
  history: WorkflowHistoryEntry[];
  estimatedCompletion?: string;
}

export interface WorkflowApprover {
  userId: string;
  name: string;
  role: string;
  status: 'pending' | 'approved' | 'rejected';
  actionDate?: string;
  comments?: string;
}

export interface WorkflowHistoryEntry {
  action: string;
  performedBy: string;
  date: string;
  comments?: string;
}

// Enhanced Utility Functions
export namespace CommercialLendingUtils {
  // ...existing code...

  export function calculateCapitalRequirement(
    exposureAmount: number,
    riskWeight: number,
    capitalRatio: number = 0.08
  ): number {
    return exposureAmount * riskWeight * capitalRatio;
  }

  export function assessConcentrationRisk(
    exposures: number[],
    totalPortfolio: number,
    concentrationLimit: number = 0.25
  ): { isRisky: boolean; concentrationRatio: number; recommendation: string } {
    const maxExposure = Math.max(...exposures);
    const concentrationRatio = maxExposure / totalPortfolio;
    
    return {
      isRisky: concentrationRatio > concentrationLimit,
      concentrationRatio,
      recommendation: concentrationRatio > concentrationLimit 
        ? 'Consider diversifying portfolio to reduce concentration risk'
        : 'Concentration risk is within acceptable limits'
    };
  }

  export function calculateExpectedLoss(
    probabilityOfDefault: number,
    lossGivenDefault: number,
    exposureAtDefault: number
  ): number {
    return probabilityOfDefault * lossGivenDefault * exposureAtDefault;
  }

  export function categorizeIndustryRisk(industryCode: string): 'low' | 'medium' | 'high' {
    // High-risk industries
    const highRiskIndustries = ['23', '72', '48', '51']; // Construction, Accommodation, Transportation, Information
    // Medium-risk industries  
    const mediumRiskIndustries = ['44', '45', '52', '53']; // Retail, Finance, Real Estate
    
    if (highRiskIndustries.includes(industryCode)) return 'high';
    if (mediumRiskIndustries.includes(industryCode)) return 'medium';
    return 'low';
  }

  export function validateRegularExpression(pattern: string, value: string): boolean {
    try {
      return new RegExp(pattern).test(value);
    } catch {
      return false;
    }
  }

  export function calculateVaR(
    returns: number[],
    confidenceLevel: number = 0.95
  ): number {
    if (returns.length === 0) return 0;
    
    const sortedReturns = [...returns].sort((a, b) => a - b);
    const index = Math.floor((1 - confidenceLevel) * sortedReturns.length);
    return sortedReturns[index] || 0;
  }
}

export default CommercialViewClient;
