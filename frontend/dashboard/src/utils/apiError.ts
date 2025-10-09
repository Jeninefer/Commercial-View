import axios from 'axios';
import { ApiError } from '../types/api';

export const toApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    return {
      message: error.response?.data?.message ?? error.message ?? 'Unexpected API error',
      statusCode: error.response?.status,
    };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: 'Unknown error' };
};
