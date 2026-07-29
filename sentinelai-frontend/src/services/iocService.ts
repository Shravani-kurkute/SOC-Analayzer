import api from './api';
import type { IocEntry, IocStats, IocExtractResult } from '@typings/ioc';

export const iocService = {
  async list(params?: {
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
    ioc_type?: string;
    severity?: string;
    status?: string;
    source_ip?: string;
  }): Promise<{ items: IocEntry[]; total: number; page: number; page_size: number; total_pages: number; has_next: boolean; has_prev: boolean }> {
    const response = await api.get('/ioc', { params });
    return response.data.data;
  },

  async get(id: string): Promise<IocEntry> {
    const response = await api.get(`/ioc/${id}`);
    return response.data.data;
  },

  async getStats(): Promise<IocStats> {
    const response = await api.get('/ioc/stats');
    return response.data.data;
  },

  async search(q: string, page?: number, page_size?: number): Promise<{ items: IocEntry[]; total: number }> {
    const response = await api.get('/ioc/search', { params: { q, page, page_size } });
    return response.data.data;
  },

  async extractFromText(text: string, source?: string): Promise<IocExtractResult> {
    const response = await api.post('/ioc/extract', null, { params: { text, source } });
    return response.data.data;
  },
};
