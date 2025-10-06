export interface ExecutiveSummary {
  totalValue: number;
  riskScore: number;
  portfolioCount: number;
  // add other properties as needed
}

export interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}