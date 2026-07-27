import api from './api'
import type {
  DashboardSummary,
  DashboardActivity,
  DashboardCharts,
  RecentAlertItem,
  RecentIncidentItem,
  RecentLogItem,
  MostActiveSourceIp,
  MostTargetedUser,
} from '@typings/dashboard'

export const dashboardService = {
  async getSummary(): Promise<DashboardSummary> {
    const response = await api.get('/dashboard/summary')
    return response.data
  },

  async getActivity(): Promise<DashboardActivity> {
    const response = await api.get('/dashboard/activity')
    return response.data
  },

  async getCharts(): Promise<DashboardCharts> {
    const response = await api.get('/dashboard/charts')
    return response.data
  },

  async getRecentAlerts(limit = 10): Promise<RecentAlertItem[]> {
    const response = await api.get('/dashboard/recent-alerts', { params: { limit } })
    return response.data
  },

  async getRecentIncidents(limit = 10): Promise<RecentIncidentItem[]> {
    const response = await api.get('/dashboard/recent-incidents', { params: { limit } })
    return response.data
  },

  async getRecentLogs(limit = 10): Promise<RecentLogItem[]> {
    const response = await api.get('/dashboard/recent-logs', { params: { limit } })
    return response.data
  },

  async getMostActiveIps(limit = 10): Promise<MostActiveSourceIp[]> {
    const response = await api.get('/dashboard/most-active-ips', { params: { limit } })
    return response.data
  },

  async getMostTargetedUsers(limit = 10): Promise<MostTargetedUser[]> {
    const response = await api.get('/dashboard/most-targeted-users', { params: { limit } })
    return response.data
  },
}
