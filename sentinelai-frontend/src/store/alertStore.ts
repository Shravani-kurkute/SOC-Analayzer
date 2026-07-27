import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Alert, AlertFilter, AlertStats } from '@typings/alert';

interface AlertState {
  alerts: Alert[];
  selectedAlert: Alert | null;
  filter: AlertFilter;
  stats: AlertStats | null;
  isLoading: boolean;
  total: number;
  page: number;
  pageSize: number;

  setAlerts: (alerts: Alert[]) => void;
  setSelectedAlert: (alert: Alert | null) => void;
  setFilter: (filter: Partial<AlertFilter>) => void;
  setStats: (stats: AlertStats) => void;
  setLoading: (loading: boolean) => void;
  setPage: (page: number) => void;
  reset: () => void;
}

const initialFilter: AlertFilter = {
  severity: [],
  status: [],
  source: [],
  dateRange: null,
  search: '',
};

export const useAlertStore = create<AlertState>()(
  devtools(
    (set) => ({
      alerts: [],
      selectedAlert: null,
      filter: initialFilter,
      stats: null,
      isLoading: false,
      total: 0,
      page: 1,
      pageSize: 25,

      setAlerts: (alerts) => set({ alerts }),
      setSelectedAlert: (selectedAlert) => set({ selectedAlert }),
      setFilter: (filter) =>
        set((state) => ({ filter: { ...state.filter, ...filter } })),
      setStats: (stats) => set({ stats }),
      setLoading: (isLoading) => set({ isLoading }),
      setPage: (page) => set({ page }),
      reset: () =>
        set({
          alerts: [],
          selectedAlert: null,
          filter: initialFilter,
          stats: null,
          page: 1,
        }),
    }),
    { name: 'alert-store' },
  ),
);
