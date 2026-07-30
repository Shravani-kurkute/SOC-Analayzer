import api from './api';
import type { ThreatIntelResult, ThreatIntelStats } from '@typings/threatIntel';

export const threatIntelService = {
  async lookup(iocType: string, iocValue: string): Promise<ThreatIntelResult> {
    const response = await api.post('/threat-intelligence/lookup', { ioc_type: iocType, ioc_value: iocValue });
    return response.data.data;
  },

  async list(params?: {
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
    ioc_type?: string;
    is_malicious?: boolean;
    q?: string;
  }): Promise<{ items: ThreatIntelResult[]; total: number; page: number; page_size: number; total_pages: number; has_next: boolean; has_prev: boolean }> {
    const response = await api.get('/threat-intelligence', { params });
    return response.data.data;
  },

  async get(id: string): Promise<ThreatIntelResult> {
    const response = await api.get(`/threat-intelligence/${id}`);
    return response.data.data;
  },

  async getStats(): Promise<ThreatIntelStats> {
    const response = await api.get('/threat-intelligence/stats');
    return response.data.data;
  },
};
