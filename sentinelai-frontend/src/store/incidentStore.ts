import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Incident, IncidentFilter } from '@typings/incident';

interface IncidentState {
  incidents: Incident[];
  selectedIncident: Incident | null;
  filter: IncidentFilter;
  isLoading: boolean;
  total: number;
  page: number;

  setIncidents: (incidents: Incident[]) => void;
  setSelectedIncident: (incident: Incident | null) => void;
  setFilter: (filter: Partial<IncidentFilter>) => void;
  setLoading: (loading: boolean) => void;
  setPage: (page: number) => void;
  reset: () => void;
}

export const useIncidentStore = create<IncidentState>()(
  devtools(
    (set) => ({
      incidents: [],
      selectedIncident: null,
      filter: {},
      isLoading: false,
      total: 0,
      page: 1,

      setIncidents: (incidents) => set({ incidents }),
      setSelectedIncident: (selectedIncident) => set({ selectedIncident }),
      setFilter: (filter) =>
        set((state) => ({ filter: { ...state.filter, ...filter } })),
      setLoading: (isLoading) => set({ isLoading }),
      setPage: (page) => set({ page }),
      reset: () =>
        set({
          incidents: [],
          selectedIncident: null,
          filter: {},
          page: 1,
        }),
    }),
    { name: 'incident-store' },
  ),
);
