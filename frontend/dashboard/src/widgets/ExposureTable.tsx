import React from 'react';
import type { ExposureTableProps } from '../types/widgets';
import { formatMetricValue } from '../utils/formatters';

const ExposureTable: React.FC<ExposureTableProps> = ({ rows, loading, error }) => {
  if (error) {
    return (
      <div role="alert" className="alert alert--error">
        <strong>Exposure insights unavailable.</strong>
        <span>{error}</span>
      </div>
    );
  }

  if (loading) {
    return <div className="table-placeholder" aria-busy aria-label="Loading exposure table" />;
  }

  if (!rows.length) {
    return <p role="status">No exposure records surfaced. Import the latest CSV to populate this view.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="data-table" aria-label="Top portfolio exposures">
        <thead>
          <tr>
            <th scope="col">Borrower</th>
            <th scope="col">Relationship Manager</th>
            <th scope="col">Outstanding</th>
            <th scope="col">Risk Score</th>
            <th scope="col">Industry</th>
            <th scope="col">Next Review</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.borrower}-${row.industry}`}>
              <th scope="row">{row.borrower}</th>
              <td>{row.relationshipManager}</td>
              <td>{formatMetricValue(row.outstanding, 'currency')}</td>
              <td>
                <span className="risk-score" aria-label={`Risk score ${row.riskScore}`}>
                  {row.riskScore.toFixed(1)}
                </span>
              </td>
              <td>{row.industry}</td>
              <td>{row.nextReview}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExposureTable;
