import { CsvPreviewRow } from './api';

export interface CsvIngestionState {
  isUploading: boolean;
  uploadError?: string;
  previewRows: CsvPreviewRow[];
  lastUploadedFileName?: string;
  lastUploadedAt?: string;
  ingestedRowCount?: number;
}

export interface CsvIngestionActions {
  beginUpload: (fileName: string) => void;
  completeUpload: (rows: CsvPreviewRow[], timestamp: string, ingested: number) => void;
  failUpload: (message: string) => void;
  resetError: () => void;
}

export type DashboardStore = {
  csvState: CsvIngestionState;
} & CsvIngestionActions;
