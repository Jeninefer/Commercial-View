import React, { useMemo } from 'react';
import { formatDistanceToNow } from 'date-fns';
import type { CsvIngestionState } from '../types/state';

interface DashboardLayoutProps {
  children: React.ReactNode;
  lastUpdated?: string;
  csvState: CsvIngestionState;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  lastUpdated,
  csvState,
}) => {
  const lastUpdatedLabel = useMemo(() => {
    if (!lastUpdated) {
      return 'moments ago';
    }

    try {
      return formatDistanceToNow(new Date(lastUpdated), {
        addSuffix: true,
      });
    } catch (error) {
      console.warn('Unable to format last updated timestamp', error);
      return 'recently';
    }
  }, [lastUpdated]);

  return (
    <div className="dashboard-layout">
      <header className="dashboard-header" role="banner">
        <div className="brand" aria-label="ABACO Commercial-View">
          <span className="brand-mark" aria-hidden>
            AB
          </span>
          <div className="brand-text">
            <span className="brand-name">ABACO Commercial-View</span>
            <span className="brand-tagline">Enterprise Lending Intelligence</span>
          </div>
        </div>
        <div className="header-meta" aria-live="polite">
          <span className={`status-dot ${csvState.isUploading ? 'status-dot--syncing' : 'status-dot--live'}`} aria-hidden />
          <span className="status-text">
            {csvState.isUploading ? 'Synchronizing portfolio data…' : 'Live data stream'}
          </span>
          <span className="last-updated">Last updated {lastUpdatedLabel}</span>
        </div>
      </header>
      <main className="dashboard-main" role="main">
        {children}
      </main>
      <footer className="dashboard-footer" role="contentinfo">
        <p>© {new Date().getFullYear()} Abaco Capital. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default DashboardLayout;
