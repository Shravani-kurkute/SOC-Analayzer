import api from './api';
import type { MitreTechnique, MitreTechniqueDetail, MitreCoverage } from '@typings/mitre';

export const mitreService = {
  async getRoot(): Promise<{ tactics: number; techniques: number; version: string }> {
    const response = await api.get('/mitre');
    return response.data.data;
  },

  async listTechniques(params?: {
    tactic?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ items: MitreTechnique[]; total: number; page: number; page_size: number; total_pages: number }> {
    const response = await api.get('/mitre/techniques', { params });
    return response.data.data;
  },

  async getTechnique(techniqueId: string): Promise<MitreTechniqueDetail> {
    const response = await api.get(`/mitre/${techniqueId}`);
    return response.data.data;
  },

  async listTactics(): Promise<{ tactic: string; tactic_id: string; technique_count: number }[]> {
    const response = await api.get('/mitre/tactics');
    return response.data.data;
  },

  async getCoverage(): Promise<MitreCoverage> {
    const response = await api.get('/mitre/coverage');
    return response.data.data;
  },

  async mapEntity(mappedType: string, mappedId: string, mappedName?: string, context?: string) {
    const response = await api.post('/mitre/map', { mapped_type: mappedType, mapped_id: mappedId, mapped_name: mappedName, context });
    return response.data.data;
  },

  async seedTechniques() {
    const response = await api.post('/mitre/seed');
    return response.data.data;
  },

  async search(q: string, page?: number, page_size?: number) {
    const response = await api.get('/mitre/search', { params: { q, page, page_size } });
    return response.data.data;
  },
};
