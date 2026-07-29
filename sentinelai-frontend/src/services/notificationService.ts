import { api } from './api'
import type { NotificationListResponse, UnreadCountResponse, NotificationPreferences } from '@typings/notification'

export const notificationService = {
  async list(params?: {
    limit?: number
    offset?: number
    unread_only?: boolean
    event_type?: string
    severity?: string
  }): Promise<NotificationListResponse> {
    const res = await api.get('/notifications', { params })
    return res.data
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const res = await api.get('/notifications/unread-count')
    return res.data
  },

  async markAsRead(id: string): Promise<void> {
    await api.post(`/notifications/${id}/read`)
  },

  async markAllAsRead(): Promise<void> {
    await api.post('/notifications/read-all')
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/notifications/${id}`)
  },

  async clearAll(): Promise<void> {
    await api.delete('/notifications')
  },

  async getPreferences(): Promise<NotificationPreferences> {
    const res = await api.get('/notifications/preferences')
    return res.data
  },

  async updatePreferences(prefs: Partial<NotificationPreferences>): Promise<void> {
    await api.put('/notifications/preferences', prefs)
  },
}
