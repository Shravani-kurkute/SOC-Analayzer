import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertService } from '@services/alertService';
import { useAlertStore } from '@store/alertStore';

function filterToParams(filter: Record<string, unknown>) {
  const params: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(filter)) {
    if (Array.isArray(value)) {
      params[key] = value.join(',');
    } else if (value !== null && value !== undefined && value !== '') {
      params[key] = value;
    }
  }
  return params;
}

export function useAlerts(params?: Record<string, unknown>) {
  const setAlerts = useAlertStore((state) => state.setAlerts);
  const setStats = useAlertStore((state) => state.setStats);
  const filter = useAlertStore((state) => state.filter);
  const page = useAlertStore((state) => state.page);
  const pageSize = useAlertStore((state) => state.pageSize);

  const queryParams = { ...filterToParams({ ...filter }), page, pageSize, ...params };

  const alertsQuery = useQuery({
    queryKey: ['alerts', filter, page, pageSize, params],
    queryFn: async () => {
      const response = await alertService.getAlerts(queryParams as Record<string, unknown>);
      if (response.data) {
        setAlerts(response.data.items);
      }
      return response;
    },
  });

  const statsQuery = useQuery({
    queryKey: ['alert-stats', filter],
    queryFn: async () => {
      const response = await alertService.getStats(filter as unknown as Record<string, unknown>);
      if (response.data) {
        setStats(response.data);
      }
      return response;
    },
    refetchInterval: 30000,
  });

  return {
    alerts: alertsQuery.data?.data?.items ?? [],
    total: alertsQuery.data?.data?.total ?? 0,
    isLoading: alertsQuery.isLoading,
    error: alertsQuery.error,
    stats: statsQuery.data?.data ?? null,
    refetch: alertsQuery.refetch,
  };
}

export function useAlert(id: string) {
  return useQuery({
    queryKey: ['alert', id],
    queryFn: () => alertService.getAlert(id),
    enabled: !!id,
  });
}

export function useUpdateAlertStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      alertService.updateAlertStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}
