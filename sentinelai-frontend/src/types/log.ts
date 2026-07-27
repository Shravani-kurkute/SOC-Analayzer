export interface LogFile {
  id: string
  original_filename: string
  source_type: string
  source_name: string | null
  size: number
  mime_type: string | null
  checksum_sha256: string
  status: string
  error_message: string | null
  uploaded_by: string | null
  upload_time: string
  processing_started_at: string | null
  processing_completed_at: string | null
  parsed_entries: number
  failed_entries: number
  tags: string[] | null
}

export interface LogUploadResponse {
  id: string
  original_filename: string
  size: number
  checksum_sha256: string
  status: string
  upload_time: string
  message: string
}

export interface LogFileListResponse {
  items: LogFile[]
  total: number
  page: number
  page_size: number
}

export interface LogStatsResponse {
  total_files: number
  total_size: number
  total_parsed_entries: number
  by_source_type: Record<string, number>
  by_status: Record<string, number>
  recent_uploads: number
  avg_file_size: number
  storage_used: string
}
