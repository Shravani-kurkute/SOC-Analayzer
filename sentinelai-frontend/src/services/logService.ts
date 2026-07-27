import api from './api'
import type { LogFile, LogFileListResponse, LogStatsResponse, LogUploadResponse } from '@typings/log'

export const logService = {
  async upload(
    file: File,
    onProgress?: (percent: number) => void,
  ): Promise<LogUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/logs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (onProgress && event.total) {
          const percent = Math.round((event.loaded * 100) / event.total)
          onProgress(percent)
        }
      },
    })
    return response.data
  },

  async list(
    page = 1,
    pageSize = 20,
    sourceType?: string,
    status?: string,
  ): Promise<LogFileListResponse> {
    const params: Record<string, string | number> = { page, page_size: pageSize }
    if (sourceType) params.source_type = sourceType
    if (status) params.status = status
    const response = await api.get('/logs', { params })
    return response.data
  },

  async get(id: string): Promise<LogFile> {
    const response = await api.get(`/logs/${id}`)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/logs/${id}`)
  },

  async getStats(): Promise<LogStatsResponse> {
    const response = await api.get('/logs/stats')
    return response.data
  },
}
