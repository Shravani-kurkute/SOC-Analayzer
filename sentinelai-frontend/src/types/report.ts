export interface ReportRequest {
  report_type: string
  title: string
  format?: string
  date_range_start?: string
  date_range_end?: string
  severity?: string
  status?: string
  mitre_technique?: string
  incident_id?: string
  analyst_id?: string
}

export interface ReportResponse {
  id: string
  report_type: string
  title: string
  format: string
  status: string
  file_path?: string
  file_size?: number
  date_range_start?: string
  date_range_end?: string
  filters?: Record<string, unknown>
  data?: Record<string, unknown>
  download_count: number
  generated_by_id?: string
  created_at: string
  created_by?: string
}

export interface ReportListItem {
  id: string
  report_type: string
  title: string
  format: string
  status: string
  file_size?: number
  download_count: number
  generated_by_id?: string
  created_at: string
  created_by?: string
}

export interface ReportListResponse {
  items: ReportListItem[]
  total: number
}

export interface ReportStats {
  total_reports: number
  reports_today: number
  most_downloaded: ReportListItem[]
  recent_reports: ReportListItem[]
}

export type ReportType = 'executive' | 'threat' | 'incident' | 'asset' | 'compliance'
export type ReportFormat = 'json' | 'csv' | 'xlsx' | 'pdf'
