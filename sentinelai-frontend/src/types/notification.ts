export interface Notification {
  id: string
  event_type: string
  title: string
  message?: string
  severity: 'critical' | 'warning' | 'info' | 'success'
  source?: string
  source_id?: string
  is_read: boolean
  created_at: string
}

export interface NotificationListResponse {
  items: Notification[]
  total: number
}

export interface UnreadCountResponse {
  count: number
}

export interface NotificationPreferences {
  email_enabled: boolean
  desktop_enabled: boolean
  slack_enabled: boolean
  discord_enabled: boolean
  teams_enabled: boolean
  telegram_enabled: boolean
  critical_only: boolean
  muted_until?: string | null
  event_subscriptions: Record<string, boolean>
}

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface LiveActivityEvent {
  type: 'notification' | 'event'
  event: string
  notification?: Notification
  data?: Record<string, unknown>
  timestamp?: string
}

export interface SystemStatus {
  websocket: WebSocketStatus
  backend: 'healthy' | 'degraded' | 'down'
  database: 'healthy' | 'degraded' | 'down'
  redis: 'healthy' | 'degraded' | 'down'
}
