import api from './api';
import type { Alert, AlertStats } from '@typings/alert';
import type { APIResponse, PaginatedResponse } from '@typings/api';

export const alertService = {
  async getAlerts(params?: Record<string, unknown>): Promise<APIResponse<PaginatedResponse<Alert>>> {
    const response = await api.get('/alerts', { params });
    return response.data;
  },

  async getAlert(id: string): Promise<APIResponse<Alert>> {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  },

  async updateAlertStatus(
    id: string,
    status: string,
  ): Promise<APIResponse<Alert>> {
    const response = await api.patch(`/alerts/${id}/status`, { status });
    return response.data;
  },

  async assignToIncident(
    alertId: string,
    incidentId: string,
  ): Promise<APIResponse<Alert>> {
    const response = await api.post(`/alerts/${alertId}/assign`, { incident_id: incidentId });
    return response.data;
  },

  async getStats(filter?: Record<string, unknown>): Promise<APIResponse<AlertStats>> {
    const response = await api.get('/alerts/stats', { params: filter });
    return response.data;
  },

  async bulkUpdateStatus(
    ids: string[],
    status: string,
  ): Promise<APIResponse<{ updated: number }>> {
    const response = await api.post('/alerts/bulk/status', { ids, status });
    return response.data;
  },

  async deleteAlert(id: string): Promise<APIResponse<null>> {
    const response = await api.delete(`/alerts/${id}`);
    return response.data;
  },
};
