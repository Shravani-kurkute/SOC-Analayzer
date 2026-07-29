export interface Incident {
  id: string
  title: string
  description: string | null
  severity: string
  status: string
  category: string | null
  alert_ids: string[]
  asset_ids: string[]
  assignee_id: string | null
  assignee_name: string | null
  closed_at: string | null
  created_at: string
  updated_at: string
  created_by: string | null
  comments: IncidentComment[]
  tasks: IncidentTask[]
  evidence: IncidentEvidence[]
  timeline: IncidentTimeline[]
}

export interface IncidentListItem {
  id: string
  title: string
  severity: string
  status: string
  category: string | null
  assignee_id: string | null
  assignee_name: string | null
  alert_count: number
  task_count: number
  task_done: number
  evidence_count: number
  created_at: string
  updated_at: string
  closed_at: string | null
}

export interface IncidentComment {
  id: string
  incident_id: string
  author_id: string | null
  author_name: string
  content: string
  is_edited: boolean
  created_at: string
  updated_at: string
}

export interface IncidentTask {
  id: string
  incident_id: string
  title: string
  description: string | null
  status: string
  priority: string
  assignee_id: string | null
  assignee_name: string | null
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface IncidentEvidence {
  id: string
  incident_id: string
  filename: string
  file_type: string
  file_size: number
  sha256: string
  uploaded_by: string
  description: string | null
  created_at: string
}

export interface IncidentTimeline {
  id: string
  incident_id: string
  action: string
  actor: string
  details: string | null
  metadata_json: Record<string, unknown> | null
  created_at: string
}

export interface IncidentFilter {
  severity?: string
  status?: string
  assignee_id?: string
  search?: string
  sort_by?: string
  sort_order?: string
}

export interface IncidentStats {
  total_incidents: number
  open_incidents: number
  critical_incidents: number
  closed_incidents: number
  by_status: Record<string, number>
  by_severity: Record<string, number>
  by_analyst: Record<string, number>
  avg_resolution_seconds: number | null
}
