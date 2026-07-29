import api from './api'
import type { AIInvestigation, AIInvestigationListItem, AIInvestigationStats } from '@typings/ai'

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

export const aiService = {
  async investigate(incidentId: string, provider?: string): Promise<AIInvestigation> {
    const response = await api.post(`/ai/investigate/${incidentId}`, provider ? { provider } : {})
    return (response.data as ApiResponse<AIInvestigation>).data
  },

  async getReport(incidentId: string): Promise<AIInvestigation> {
    const response = await api.get(`/ai/report/${incidentId}`)
    return (response.data as ApiResponse<AIInvestigation>).data
  },

  async listHistory(page = 1, pageSize = 20): Promise<PaginatedResponse<AIInvestigationListItem>> {
    const response = await api.get('/ai/history', { params: { page, page_size: pageSize } })
    return (response.data as ApiResponse<PaginatedResponse<AIInvestigationListItem>>).data
  },

  async deleteHistory(investigationId: string): Promise<void> {
    await api.delete(`/ai/history/${investigationId}`)
  },

  async getStats(): Promise<AIInvestigationStats> {
    const response = await api.get('/ai/stats')
    return (response.data as ApiResponse<AIInvestigationStats>).data
  },
}
