export interface DashboardSummary {
  total_logs_processed: number
  active_incidents: number
  critical_alerts: number
  high_alerts: number
  medium_alerts: number
  low_alerts: number
  threat_score: number
  assets_monitored: number
  threat_intel_total?: number
  threat_intel_malicious?: number
  ai_investigations?: number
  avg_ai_confidence?: number
}

export interface ActivityPoint {
  timestamp: string
  value: number
}

export interface DashboardActivity {
  timeline: ActivityPoint[]
}

export interface SeverityDistribution {
  name: string
  value: number
  fill?: string
}

export interface AttackTypeCount {
  name: string
  count: number
}

export interface TopSourceIp {
  ip: string
  count: number
  country: string | null
}

export interface MitreDistribution {
  tactic: string
  count: number
}

export interface CountryDistribution {
  country: string
  count: number
}

export interface DashboardCharts {
  attack_timeline: ActivityPoint[]
  alerts_by_severity: SeverityDistribution[]
  attack_types: AttackTypeCount[]
  top_source_ips: TopSourceIp[]
  mitre_distribution: MitreDistribution[]
  country_distribution: CountryDistribution[]
}

export interface RecentAlertItem {
  id: string
  title: string
  severity: string
  status: string
  source: string | null
  source_ip: string | null
  timestamp: string
  score: number
}

export interface RecentIncidentItem {
  id: string
  title: string
  severity: string
  status: string
  category: string | null
  assignee_id: string | null
  created_at: string
  alert_count: number
}

export interface RecentLogItem {
  id: string
  timestamp: string
  source_ip: string | null
  destination_ip: string | null
  action: string | null
  protocol: string | null
  log_source: string | null
  threat_score: number | null
}

export interface MostActiveSourceIp {
  ip: string
  country: string | null
  log_count: number
  alert_count: number
}

export interface MostTargetedUser {
  user_id: string
  email: string
  alert_count: number
}
