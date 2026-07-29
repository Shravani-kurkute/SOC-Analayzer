import { api } from './api'
import type { ReportRequest, ReportResponse, ReportListResponse, ReportStats } from '@typings/report'

export const reportService = {
  async generate(req: ReportRequest): Promise<ReportResponse> {
    const res = await api.post('/reports/generate', req)
    return res.data
  },

  async list(limit = 50, offset = 0): Promise<ReportListResponse> {
    const res = await api.get('/reports', { params: { limit, offset } })
    return res.data
  },

  async get(id: string): Promise<ReportResponse> {
    const res = await api.get(`/reports/${id}`)
    return res.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/reports/${id}`)
  },

  downloadUrl(id: string): string {
    return `${api.defaults.baseURL}/reports/download/${id}`
  },

  async getStats(): Promise<ReportStats> {
    const res = await api.get('/reports/stats')
    return res.data
  },

  async getDashboardStats(): Promise<ReportStats> {
    const res = await api.get('/dashboard/report-stats')
    return res.data
  },
}
