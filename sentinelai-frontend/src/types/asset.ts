export interface Asset {
  id: string;
  hostname: string;
  ip_address: string | null;
  mac_address: string | null;
  os: string | null;
  os_version: string | null;
  asset_type: string;
  criticality: string;
  environment: string | null;
  status: string;
  tags: string[] | null;
  vulnerability_count: number;
  open_ports: number;
  last_seen: string | null;
  location: string | null;
  department: string | null;
  owner: string | null;
  vendor: string | null;
  serial_number: string | null;
  notes: string | null;
  risk_score: number;
  discovery_source: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
}

export interface AssetListItem {
  id: string;
  hostname: string;
  ip_address: string | null;
  os: string | null;
  asset_type: string;
  criticality: string;
  status: string;
  risk_score: number;
  department: string | null;
  owner: string | null;
  vulnerability_count: number;
  last_seen: string | null;
  created_at: string;
}

export interface AssetDetail extends Asset {
  risk_details: AssetRiskDetail | null;
  incident_count: number;
  alert_count: number;
  ioc_count: number;
  threat_intel_count: number;
  ai_report_count: number;
  relationships: AssetRelationshipItem[];
  history: AssetHistoryItem[];
}

export interface AssetRiskDetail {
  risk_score: number;
  open_incidents: number;
  critical_alerts: number;
  threat_intel_matches: number;
  cve_count: number;
  exposure_score: number;
  criticality_weight: number;
  calculated_at: string;
}

export interface AssetRelationshipItem {
  id: string;
  source_asset_id: string;
  target_asset_id: string;
  relationship_type: string;
  direction: string;
  target: {
    id: string;
    hostname?: string;
    ip_address?: string;
    asset_type?: string;
    criticality?: string;
  };
}

export interface AssetHistoryItem {
  id: string;
  asset_id: string;
  field_name: string;
  old_value: string | null;
  new_value: string | null;
  changed_by: string | null;
  created_at: string;
}

export interface AssetFilter {
  search?: string;
  asset_type?: string;
  criticality?: string;
  status?: string;
  department?: string;
  owner?: string;
  os?: string;
  risk_level?: string;
  tag?: string;
  sort_by?: string;
  sort_order?: string;
}

export interface AssetStats {
  total_assets: number;
  healthy_assets: number;
  critical_assets: number;
  offline_assets: number;
  high_risk_assets: number;
  by_department: Record<string, number>;
  by_os: Record<string, number>;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_criticality: Record<string, number>;
  risk_distribution: Record<string, number>;
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
