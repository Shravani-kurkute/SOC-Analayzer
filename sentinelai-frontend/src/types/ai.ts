export interface AIInvestigation {
  id: string
  incident_id: string
  provider: string
  summary: string | null
  attack_explanation: string | null
  timeline_data: TimelineEvent[] | null
  root_cause: string | null
  mitre_explanation: string | null
  ioc_summary: string | null
  risk_explanation: string | null
  recommendations: Recommendation[] | null
  containment: string | null
  recovery: string | null
  hunting_queries: HuntingQuery[] | null
  false_positive_probability: number | null
  confidence_score: number | null
  tokens_used: number | null
  latency_ms: number | null
  error: string | null
  created_at: string
  prompt: string | null
}

export interface TimelineEvent {
  timestamp: string
  event: string
  source: string
  detail: string
}

export interface Recommendation {
  priority: 'critical' | 'high' | 'medium' | 'low'
  action: string
  details: string
}

export interface HuntingQuery {
  type: string
  query: string
  description: string
}

export interface AIInvestigationListItem {
  id: string
  incident_id: string
  incident_title: string | null
  provider: string
  summary: string | null
  confidence_score: number | null
  tokens_used: number | null
  latency_ms: number | null
  error: string | null
  created_at: string
}

export interface AIInvestigationStats {
  total_investigations: number
  average_confidence: number
  average_latency_ms: number
  provider_usage: Record<string, number>
  recent_investigations: AIInvestigationListItem[]
}
