export interface Alert {
  id: string;
  title: string;
  description: string | null;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'informational';
  status: 'open' | 'acknowledged' | 'investigating' | 'resolved' | 'false_positive';
  source: string | null;
  source_ip: string | null;
  destination_ip: string | null;
  source_port: number | null;
  destination_port: number | null;
  protocol: string | null;
  mitre_technique_id: string | null;
  mitre_tactic: string | null;
  rule_id: string | null;
  rule_name: string | null;
  score: number;
  raw_data: Record<string, unknown> | null;
  enriched_data: Record<string, unknown> | null;
  tags: string[] | null;
  asset_ids: string[] | null;
  country: string | null;
  city: string | null;
  correlation_group_id: string | null;
  recommendation: string | null;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  incident_id: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
}

export interface AlertListResponse {
  items: Alert[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AlertStatsResponse {
  total: number;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  by_rule: Record<string, number>;
  top_source_ips: Array<{ ip: string; count: number }>;
  avg_score: number;
  recent_trend: Array<{ date: string; count: number }>;
}
