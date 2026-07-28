import api from './api';
import type {
  CorrelationGroup,
  CorrelationGroupList,
  CorrelationStats,
  CorrelationRunResult,
} from '@typings/correlation';

export const correlationService = {
  async runCorrelation(ruleName?: string): Promise<CorrelationRunResult> {
    const params = ruleName ? { rule_name: ruleName } : {};
    const response = await api.post('/correlation/run', null, { params });
    return response.data;
  },

  async runAllCorrelations(): Promise<CorrelationRunResult> {
    const response = await api.post('/correlation/run-all');
    return response.data;
  },

  async getGroups(params?: {
    group_type?: string;
    status?: string;
    source_ip?: string;
    username?: string;
    min_risk?: number;
    limit?: number;
    offset?: number;
  }): Promise<CorrelationGroupList[]> {
    const response = await api.get('/correlation', { params });
    return response.data;
  },

  async getGroup(id: string): Promise<CorrelationGroup> {
    const response = await api.get(`/correlation/${id}`);
    return response.data;
  },

  async getStats(): Promise<CorrelationStats> {
    const response = await api.get('/correlation/stats');
    return response.data;
  },
};
