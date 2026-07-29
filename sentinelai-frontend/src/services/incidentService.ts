import api from './api'
import type {
  Incident, IncidentListItem, IncidentComment, IncidentTask,
  IncidentEvidence, IncidentStats, IncidentFilter,
} from '@typings/incident'

interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export const incidentService = {
  async getIncidents(params?: IncidentFilter & { page?: number; page_size?: number }): Promise<ApiResponse<PaginatedData<IncidentListItem>>> {
    const response = await api.get('/incidents', { params })
    return response.data
  },

  async getIncident(id: string): Promise<Incident> {
    const response = await api.get(`/incidents/${id}`)
    return (response.data as ApiResponse<Incident>).data
  },

  async getStats(): Promise<IncidentStats> {
    const response = await api.get('/incidents/stats')
    return (response.data as ApiResponse<IncidentStats>).data
  },

  async createIncident(data: {
    title: string; severity?: string; description?: string;
    category?: string; alert_ids?: string[]; asset_ids?: string[]
  }): Promise<Incident> {
    const response = await api.post('/incidents', data)
    return (response.data as ApiResponse<Incident>).data
  },

  async updateIncident(id: string, data: Partial<{
    title: string; description: string; severity: string; status: string;
    category: string; alert_ids: string[]; asset_ids: string[]
  }>): Promise<Incident> {
    const response = await api.put(`/incidents/${id}`, data)
    return (response.data as ApiResponse<Incident>).data
  },

  async assignIncident(id: string, userId: string): Promise<Incident> {
    const response = await api.post(`/incidents/${id}/assign`, { user_id: userId })
    return (response.data as ApiResponse<Incident>).data
  },

  async closeIncident(id: string, resolution?: string, notes?: string): Promise<Incident> {
    const response = await api.post(`/incidents/${id}/close`, { resolution, notes })
    return (response.data as ApiResponse<Incident>).data
  },

  async addComment(id: string, content: string): Promise<IncidentComment> {
    const response = await api.post(`/incidents/${id}/comment`, { content })
    return (response.data as ApiResponse<IncidentComment>).data
  },

  async editComment(incidentId: string, commentId: string, content: string): Promise<IncidentComment> {
    const response = await api.put(`/incidents/${incidentId}/comment/${commentId}`, { content })
    return (response.data as ApiResponse<IncidentComment>).data
  },

  async deleteComment(incidentId: string, commentId: string): Promise<void> {
    await api.delete(`/incidents/${incidentId}/comment/${commentId}`)
  },

  async createTask(incidentId: string, data: {
    title: string; description?: string; priority?: string;
    assignee_id?: string; due_date?: string
  }): Promise<IncidentTask> {
    const response = await api.post(`/incidents/${incidentId}/task`, data)
    return (response.data as ApiResponse<IncidentTask>).data
  },

  async updateTask(incidentId: string, taskId: string, data: Partial<{
    title: string; description: string; status: string; priority: string;
    assignee_id: string; due_date: string
  }>): Promise<IncidentTask> {
    const response = await api.patch(`/incidents/${incidentId}/task/${taskId}`, data)
    return (response.data as ApiResponse<IncidentTask>).data
  },

  async uploadEvidence(incidentId: string, file: File, description?: string): Promise<IncidentEvidence> {
    const formData = new FormData()
    formData.append('file', file)
    if (description) formData.append('description', description)
    const response = await api.post(`/incidents/${incidentId}/evidence`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return (response.data as ApiResponse<IncidentEvidence>).data
  },

  async deleteEvidence(incidentId: string, evidenceId: string): Promise<void> {
    await api.delete(`/incidents/${incidentId}/evidence/${evidenceId}`)
  },
}
