import { useQuery } from '@tanstack/react-query';
import { fetchRiskExposure } from '../api/dashboard';
import { ApiError, RiskExposureResponse } from '../types/api';
import { toApiError } from '../utils/apiError';

const QUERY_KEY = ['risk-exposure'];

export const useRiskExposure = () =>
  useQuery<RiskExposureResponse, ApiError>({
    queryKey: QUERY_KEY,
    queryFn: async () => {
      try {
        return await fetchRiskExposure();
      } catch (error) {
        throw toApiError(error);
      }
    },
    retry: 1,
    refetchInterval: 1000 * 60 * 15,
    suspense: false,
  });
