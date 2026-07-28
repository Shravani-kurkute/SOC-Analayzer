import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertService } from '@services/alertService';

export function useAlerts(params?: Record<string, unknown>) {
  const queryParams = { page: 1, page_size: 20, sort_by: 'created_at', sort_order: 'desc', ...params };

  const alertsQuery = useQuery({
    queryKey: ['alerts', queryParams],
    queryFn: () => alertService.getAlerts(queryParams),
    refetchInterval: 15_000,
  });

  const statsQuery = useQuery({
    queryKey: ['alert-stats'],
    queryFn: () => alertService.getStats(),
    refetchInterval: 30_000,
  });

  return {
    alerts: alertsQuery.data?.items ?? [],
    total: alertsQuery.data?.total ?? 0,
    page: alertsQuery.data?.page ?? 1,
    totalPages: alertsQuery.data?.total_pages ?? 1,
    isLoading: alertsQuery.isLoading,
    error: alertsQuery.error,
    stats: statsQuery.data ?? null,
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
      alertService.updateAlert(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}
