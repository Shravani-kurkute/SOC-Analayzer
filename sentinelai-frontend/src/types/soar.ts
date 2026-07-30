export interface Playbook {
  id: string;
  name: string;
  description: string | null;
  playbook_type: string;
  severity: string;
  category: string | null;
  tags: string[] | null;
  is_template: boolean;
  is_active: boolean;
  steps: PlaybookStep[];
  config: Record<string, any> | null;
  execution_count: number;
  avg_execution_time: number;
  success_rate: number;
  created_at: string;
  updated_at: string;
  created_by: string | null;
}

export interface PlaybookListItem {
  id: string;
  name: string;
  playbook_type: string;
  severity: string;
  category: string | null;
  is_template: boolean;
  is_active: boolean;
  execution_count: number;
  success_rate: number;
  created_at: string;
}

export interface PlaybookStep {
  index: number;
  name: string;
  action: string;
  config: Record<string, any>;
  type: 'action' | 'condition' | 'delay' | 'approval' | 'loop';
}

export interface PlaybookExecution {
  id: string;
  playbook_id: string;
  playbook_name: string;
  incident_id: string | null;
  status: string;
  current_step: number;
  total_steps: number;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  triggered_by: string | null;
  error_message: string | null;
  failed_step: number | null;
  execution_data: Record<string, any> | null;
  ai_summary: string | null;
  created_at: string;
}

export interface PlaybookExecutionLog {
  id: string;
  execution_id: string;
  step_index: number;
  step_name: string;
  action_type: string;
  status: string;
  message: string | null;
  duration_ms: number | null;
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  error: string | null;
  created_at: string;
}

export interface ApprovalRequest {
  id: string;
  playbook_id: string;
  execution_id: string;
  incident_id: string | null;
  step_index: number;
  action_type: string;
  requested_by: string | null;
  approved_by: string | null;
  status: string;
  reason: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface PlaybookStats {
  total_playbooks: number;
  active_playbooks: number;
  executions_today: number;
  total_executions: number;
  success_rate: number;
  avg_execution_time_ms: number;
  pending_approvals: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  recent_executions: { id: string; playbook_name: string; status: string; created_at: string }[];
}

export interface ActionDefinition {
  name: string;
  description: string;
}

export interface TemplateDefinition {
  type: string;
  steps: number;
  name: string;
}

export interface ExecuteResponse {
  execution_id: string;
  status: string;
  message: string;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}
