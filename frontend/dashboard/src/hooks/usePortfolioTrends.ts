import { useQuery } from '@tanstack/react-query';
import { fetchPortfolioTrends } from '../api/dashboard';
import { ApiError, PortfolioTrendResponse } from '../types/api';
import { toApiError } from '../utils/apiError';

const QUERY_KEY = ['portfolio-trends'];

export const usePortfolioTrends = () =>
  useQuery<PortfolioTrendResponse, ApiError>({
    queryKey: QUERY_KEY,
    queryFn: async () => {
      try {
        return await fetchPortfolioTrends();
      } catch (error) {
        throw toApiError(error);
      }
    },
    retry: 1,
    refetchInterval: 1000 * 60 * 10,
    suspense: false,
  });
