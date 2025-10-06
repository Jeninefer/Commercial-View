import React, { useState } from 'react';
import type { CsvUploaderProps } from '../types/widgets';

const CsvUploader: React.FC<CsvUploaderProps> = ({ onUpload, state, onDismissError }) => {
  const [replaceExisting, setReplaceExisting] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const [file] = Array.from(event.target.files ?? []);
    if (!file) {
      return;
    }

    await onUpload(file, replaceExisting);
    event.target.value = '';
  };

  const lastUploadedLabel = state.lastUploadedAt
    ? new Date(state.lastUploadedAt).toLocaleString()
    : undefined;

  return (
    <div className="csv-uploader">
      <label className="csv-uploader__label" htmlFor="portfolio-upload">
        Upload CSV
      </label>
      <input
        id="portfolio-upload"
        name="portfolio-upload"
        type="file"
        accept=".csv"
        className="csv-uploader__input"
        onChange={handleFileChange}
        aria-describedby="csv-upload-help"
        disabled={state.isUploading}
      />
      <div className="csv-uploader__controls">
        <label className="csv-uploader__toggle">
          <input
            type="checkbox"
            checked={replaceExisting}
            onChange={(event) => setReplaceExisting(event.target.checked)}
            disabled={state.isUploading}
          />
          Replace existing records
        </label>
        {state.isUploading && <span className="csv-uploader__status">Uploading…</span>}
      </div>
      <p id="csv-upload-help" className="csv-uploader__help">
        Accepts ABACO-formatted portfolio CSV exports with headers.
      </p>

      {state.uploadError && (
        <div role="alert" className="alert alert--error csv-uploader__alert">
          <div>
            <strong>Upload failed.</strong> {state.uploadError}
          </div>
          <button type="button" className="alert__close" onClick={onDismissError}>
            Dismiss
          </button>
        </div>
      )}

      {state.previewRows.length > 0 && (
        <div className="csv-preview" role="region" aria-live="polite">
          <h3 className="csv-preview__title">Latest ingest</h3>
          <p className="csv-preview__meta">
            Ingested{' '}
            <strong>
              {new Intl.NumberFormat('en-US').format(
                state.ingestedRowCount ?? state.previewRows.length,
              )}
            </strong>{' '}
            rows from {state.lastUploadedFileName ?? 'uploaded file'}
            {lastUploadedLabel && (
              <>
                {' '}
                on{' '}
                <time dateTime={state.lastUploadedAt}>{lastUploadedLabel}</time>
              </>
            )}
            .
          </p>
          <div className="csv-preview__table-wrapper">
            <table className="data-table data-table--compact">
              <thead>
                <tr>
                  {Object.keys(state.previewRows[0]).map((key) => (
                    <th key={key} scope="col">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {state.previewRows.slice(0, 3).map((row, rowIndex) => (
                  <tr key={`preview-${rowIndex}`}>
                    {Object.entries(row).map(([key, value]) => (
                      <td key={key}>{value as React.ReactNode}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default CsvUploader;
