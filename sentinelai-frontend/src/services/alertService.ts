import api from './api';
import type { Alert, AlertListResponse, AlertStatsResponse } from '@typings/alert';

export const alertService = {
  async getAlerts(params?: Record<string, unknown>): Promise<AlertListResponse> {
    const response = await api.get('/alerts', { params });
    return response.data;
  },

  async getAlert(id: string): Promise<Alert> {
    const response = await api.get(`/alerts/${id}`);
    return response.data;
  },

  async updateAlert(id: string, data: Record<string, unknown>): Promise<Alert> {
    const response = await api.patch(`/alerts/${id}`, data);
    return response.data;
  },

  async getStats(): Promise<AlertStatsResponse> {
    const response = await api.get('/alerts/stats');
    return response.data;
  },

  async deleteAlert(id: string): Promise<void> {
    await api.delete(`/alerts/${id}`);
  },
};
