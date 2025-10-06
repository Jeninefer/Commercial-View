import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { DashboardStoreProvider } from './state/dashboardStore';
import './styles/global.css';

const container = document.getElementById('root');

if (!container) {
  throw new Error('Root element with id "root" was not found.');
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60, // 1 minute caching for responsive UX
    },
  },
});

const root = ReactDOM.createRoot(container);

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <DashboardStoreProvider>
        <App />
      </DashboardStoreProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
