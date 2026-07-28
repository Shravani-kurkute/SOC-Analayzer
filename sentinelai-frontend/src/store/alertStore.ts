import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Alert } from '@typings/alert';

interface AlertState {
  alerts: Alert[];
  selectedAlert: Alert | null;
  isLoading: boolean;
  total: number;
  page: number;
  pageSize: number;

  setAlerts: (alerts: Alert[]) => void;
  setSelectedAlert: (alert: Alert | null) => void;
  setLoading: (loading: boolean) => void;
  setPage: (page: number) => void;
  reset: () => void;
}

export const useAlertStore = create<AlertState>()(
  devtools(
    (set) => ({
      alerts: [],
      selectedAlert: null,
      isLoading: false,
      total: 0,
      page: 1,
      pageSize: 25,

      setAlerts: (alerts) => set({ alerts }),
      setSelectedAlert: (selectedAlert) => set({ selectedAlert }),
      setLoading: (isLoading) => set({ isLoading }),
      setPage: (page) => set({ page }),
      reset: () =>
        set({
          alerts: [],
          selectedAlert: null,
          page: 1,
        }),
    }),
    { name: 'alert-store' },
  ),
);
