import { useCallback } from 'react';
import { uploadPortfolioCsv } from '../api/dashboard';
import { useDashboardStore } from '../state/dashboardStore';
import { toApiError } from '../utils/apiError';

export const useCsvIngestion = () => {
  const state = useDashboardStore((store) => store.csvState);
  const beginUpload = useDashboardStore((store) => store.beginUpload);
  const completeUpload = useDashboardStore((store) => store.completeUpload);
  const failUpload = useDashboardStore((store) => store.failUpload);
  const resetError = useDashboardStore((store) => store.resetError);

  const ingestCsv = useCallback(
    async (file: File, replaceExisting?: boolean) => {
      beginUpload(file.name);
      try {
        const response = await uploadPortfolioCsv({ file, replaceExisting });
        completeUpload(response.preview, response.lastUpdated, response.ingestedRows);
      } catch (error) {
        const apiError = toApiError(error);
        failUpload(apiError.message);
      }
    },
    [beginUpload, completeUpload, failUpload],
  );

  return { state, ingestCsv, resetError };
};
