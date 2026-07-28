export interface CorrelationEvent {
  id: string
  group_id: string
  parsed_event_id: string | null
  log_entry_id: string | null
  event_type: string
  event_source: string | null
  source_ip: string | null
  destination_ip: string | null
  username: string | null
  timestamp: string
  action: string | null
  severity: string | null
  risk_score: number | null
  raw_message: string | null
  metadata: Record<string, unknown> | null
  created_at: string
}

export interface CorrelationGroup {
  id: string
  correlation_id: string
  group_type: string
  source_ip: string | null
  destination_ip: string | null
  username: string | null
  hostname: string | null
  session_id: string | null
  start_time: string
  end_time: string
  event_count: number
  risk_score: number
  status: string
  attack_chain: string[] | null
  metadata: Record<string, unknown> | null
  description: string | null
  created_at: string
  updated_at: string
  events: CorrelationEvent[]
}

export interface CorrelationGroupList {
  id: string
  correlation_id: string
  group_type: string
  source_ip: string | null
  destination_ip: string | null
  username: string | null
  hostname: string | null
  start_time: string
  end_time: string
  event_count: number
  risk_score: number
  status: string
  attack_chain: string[] | null
  description: string | null
  created_at: string
  updated_at: string
}

export interface CorrelationStats {
  total_groups: number
  open_groups: number
  avg_risk_score: number
  total_events_correlated: number
  groups_by_type: Record<string, number>
  groups_by_status: Record<string, number>
}

export interface CorrelationRunResult {
  groups_created: number
  events_correlated: number
  message: string
}

export interface TimelineEntry {
  sequence: number
  timestamp: string
  event_id: string
  event_type: string
  action: string | null
  source_ip: string | null
  destination_ip: string | null
  username: string | null
  severity: string | null
  risk_score: number | null
  raw_message: string
  phase: string | null
}

export interface AttackChainPhase {
  phase: string
  events: TimelineEntry[]
  count: number
  max_severity: string
}

export interface EventTreeNode {
  events: CorrelationEvent[]
  count: number
  action_types: Record<string, number>
  severity_distribution: Record<string, number>
  time_span: { start: string | null; end: string | null }
}

export interface EventTree {
  source_groups: Record<string, EventTreeNode>
  total_events: number
}

export interface TimelineData {
  timeline: TimelineEntry[]
  attack_chain: AttackChainPhase[]
  event_tree: EventTree
}
