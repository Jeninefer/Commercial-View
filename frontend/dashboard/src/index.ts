import { ExecutiveSummary, ApiResponse } from './types';

// Proper state management for API data
const initialState: ApiResponse<ExecutiveSummary> = {
  data: null,
  loading: false,
  error: null
};

// Usage
let executiveSummary: ApiResponse<ExecutiveSummary> = initialState;