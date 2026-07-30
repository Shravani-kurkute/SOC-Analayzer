import api from './api';
import type {
  ApiResponse,
  Asset,
  AssetDetail,
  AssetListItem,
  AssetStats,
  PaginatedData,
  AssetFilter,
} from '@typings/asset';

export const assetService = {
  async getAssets(params?: AssetFilter & { page?: number; page_size?: number }): Promise<ApiResponse<PaginatedData<AssetListItem>>> {
    const response = await api.get('/assets', { params });
    return response.data;
  },

  async getAsset(id: string): Promise<AssetDetail> {
    const response = await api.get(`/assets/${id}`);
    return (response.data as ApiResponse<AssetDetail>).data;
  },

  async createAsset(data: Partial<Asset>): Promise<Asset> {
    const response = await api.post('/assets', data);
    return (response.data as ApiResponse<Asset>).data;
  },

  async updateAsset(id: string, data: Partial<Asset>): Promise<Asset> {
    const response = await api.put(`/assets/${id}`, data);
    return (response.data as ApiResponse<Asset>).data;
  },

  async deleteAsset(id: string): Promise<void> {
    await api.delete(`/assets/${id}`);
  },

  async getStats(): Promise<AssetStats> {
    const response = await api.get('/assets/stats');
    return (response.data as ApiResponse<AssetStats>).data;
  },

  async searchAssets(q: string, page?: number, page_size?: number): Promise<ApiResponse<PaginatedData<AssetListItem>>> {
    const response = await api.get('/assets/search', { params: { q, page, page_size } });
    return response.data;
  },

  async getAssetIncidents(id: string): Promise<any[]> {
    const response = await api.get(`/assets/${id}/incidents`);
    return (response.data as ApiResponse<any[]>).data;
  },

  async getAssetAlerts(id: string): Promise<any[]> {
    const response = await api.get(`/assets/${id}/alerts`);
    return (response.data as ApiResponse<any[]>).data;
  },

  async getAssetIocs(id: string): Promise<any[]> {
    const response = await api.get(`/assets/${id}/ioc`);
    return (response.data as ApiResponse<any[]>).data;
  },

  async getAssetThreatIntel(id: string): Promise<any[]> {
    const response = await api.get(`/assets/${id}/threat-intel`);
    return (response.data as ApiResponse<any[]>).data;
  },

  async getAssetAiReports(id: string): Promise<any[]> {
    const response = await api.get(`/assets/${id}/ai-reports`);
    return (response.data as ApiResponse<any[]>).data;
  },

  async createRelationship(sourceAssetId: string, targetAssetId: string, relationshipType: string, metadata?: Record<string, any>): Promise<any> {
    const response = await api.post('/assets/relationships', {
      source_asset_id: sourceAssetId,
      target_asset_id: targetAssetId,
      relationship_type: relationshipType,
      metadata_json: metadata,
    });
    return response.data;
  },

  async importCsv(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/assets/import/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async importJson(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/assets/import/json', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
