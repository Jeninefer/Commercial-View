import { useQuery } from '@tanstack/react-query';
import { fetchExecutiveSummary } from '../api/dashboard';
import { ApiError, ExecutiveSummaryResponse } from '../types/api';
import { toApiError } from '../utils/apiError';

const QUERY_KEY = ['executive-summary'];

export const useExecutiveSummary = () =>
  useQuery<ExecutiveSummaryResponse, ApiError>({
    queryKey: QUERY_KEY,
    queryFn: async () => {
      try {
        return await fetchExecutiveSummary();
      } catch (error) {
        throw toApiError(error);
      }
    },
    retry: 1,
    select: (response) => response,
    refetchInterval: 1000 * 60 * 5,
    suspense: false,
  });

export const getExecutiveSummaryError = (error: unknown): ApiError => toApiError(error);
