import React from 'react';
import type { RiskDistributionTableProps } from '../types/widgets';
import { formatMetricValue } from '../utils/formatters';

const RiskDistributionTable: React.FC<RiskDistributionTableProps> = ({
  rows,
  loading,
  error,
}) => {
  if (error) {
    return (
      <div role="alert" className="alert alert--error">
        <strong>Risk analytics unavailable.</strong>
        <span>{error}</span>
      </div>
    );
  }

  if (loading) {
    return <div className="table-placeholder" aria-busy aria-label="Loading risk distribution" />;
  }

  if (!rows.length) {
    return <p role="status">No risk distribution data available. Upload the latest CSV to refresh analytics.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="data-table" aria-label="Risk distribution by portfolio segment">
        <thead>
          <tr>
            <th scope="col">Segment</th>
            <th scope="col">Outstanding</th>
            <th scope="col">Delinquency</th>
            <th scope="col">Loss Given Default</th>
            <th scope="col">Risk Level</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.segment}>
              <th scope="row">{row.segment}</th>
              <td>{formatMetricValue(row.outstanding, 'currency')}</td>
              <td>{(row.delinquencyRate * 100).toFixed(2)}%</td>
              <td>{(row.lossGivenDefault * 100).toFixed(1)}%</td>
              <td>
                <span className={`risk-pill risk-pill--${row.riskLevel.toLowerCase()}`}>
                  {row.riskLevel}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RiskDistributionTable;
