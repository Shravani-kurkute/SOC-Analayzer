import api from './api';

export const aiService = {
  async analyzeAlert(alertId: string) {
    const response = await api.post('/ai/analyze', { alert_id: alertId });
    return response.data;
  },

  async analyzeIncident(incidentId: string) {
    const response = await api.post('/ai/analyze', { incident_id: incidentId });
    return response.data;
  },

  async chat(message: string, context?: Record<string, unknown>) {
    const response = await api.post('/ai/chat', { message, context });
    return response.data;
  },

  async summarize(text: string) {
    const response = await api.post('/ai/summarize', { text });
    return response.data;
  },

  async enrichIndicator(indicator: string, type: string) {
    const response = await api.post('/ai/enrich', { indicator, type });
    return response.data;
  },

  async generateRules(description: string) {
    const response = await api.post('/ai/generate-rules', { description });
    return response.data;
  },
};
