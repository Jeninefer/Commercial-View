import React, { createContext, useContext, useRef } from 'react';
import { StoreApi, useStore } from 'zustand';
import { createStore } from 'zustand/vanilla';
import type { DashboardStore } from '../types/state';

const createDashboardStore = () =>
  createStore<DashboardStore>((set) => ({
    csvState: {
      isUploading: false,
      previewRows: [],
    },
    beginUpload: (fileName) =>
      set((state) => ({
        csvState: {
          ...state.csvState,
          isUploading: true,
          uploadError: undefined,
          lastUploadedFileName: fileName,
        },
      })),
    completeUpload: (rows, timestamp, ingested) =>
      set((state) => ({
        csvState: {
          ...state.csvState,
          isUploading: false,
          previewRows: rows,
          uploadError: undefined,
          lastUploadedAt: timestamp,
          ingestedRowCount: ingested,
        },
      })),
    failUpload: (message) =>
      set((state) => ({
        csvState: {
          ...state.csvState,
          isUploading: false,
          uploadError: message,
        },
      })),
    resetError: () =>
      set((state) => ({
        csvState: {
          ...state.csvState,
          uploadError: undefined,
        },
      })),
  }));

const DashboardStoreContext = createContext<StoreApi<DashboardStore> | null>(null);

export const DashboardStoreProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const storeRef = useRef<StoreApi<DashboardStore>>();
  if (!storeRef.current) {
    storeRef.current = createDashboardStore();
  }

  return (
    <DashboardStoreContext.Provider value={storeRef.current}>
      {children}
    </DashboardStoreContext.Provider>
  );
};

export const useDashboardStore = <T,>(selector: (state: DashboardStore) => T): T => {
  const store = useContext(DashboardStoreContext);
  if (!store) {
    throw new Error('useDashboardStore must be used within a DashboardStoreProvider');
  }

  return useStore(store, selector);
};
