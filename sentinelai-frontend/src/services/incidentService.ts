import api from './api';

export const incidentService = {
  async getIncidents(params?: Record<string, unknown>) {
    const response = await api.get('/incidents', { params });
    return response.data;
  },

  async getIncident(id: string) {
    const response = await api.get(`/incidents/${id}`);
    return response.data;
  },

  async createIncident(data: { alertIds: string[]; title: string; severity: string }) {
    const response = await api.post('/incidents', data);
    return response.data;
  },

  async updateIncident(id: string, data: Record<string, unknown>) {
    const response = await api.patch(`/incidents/${id}`, data);
    return response.data;
  },

  async updateStatus(id: string, status: string) {
    const response = await api.patch(`/incidents/${id}/status`, { status });
    return response.data;
  },

  async addNote(id: string, content: string, isPrivate = false) {
    const response = await api.post(`/incidents/${id}/notes`, { content, is_private: isPrivate });
    return response.data;
  },

  async assignAnalyst(id: string, userId: string) {
    const response = await api.post(`/incidents/${id}/assign`, { user_id: userId });
    return response.data;
  },
};
