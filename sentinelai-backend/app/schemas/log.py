from datetime import datetime
from app.schemas.base import BaseSchema


class LogFileResponse(BaseSchema):
    id: str
    original_filename: str
    source_type: str
    source_name: str | None
    size: int
    mime_type: str | None
    checksum_sha256: str
    status: str
    error_message: str | None
    uploaded_by: str | None
    upload_time: datetime
    processing_started_at: datetime | None
    processing_completed_at: datetime | None
    parsed_entries: int
    failed_entries: int
    tags: list[str] | None


class LogFileListResponse(BaseSchema):
    items: list[LogFileResponse]
    total: int
    page: int
    page_size: int


class LogUploadResponse(BaseSchema):
    id: str
    original_filename: str
    size: int
    checksum_sha256: str
    status: str
    upload_time: datetime
    message: str


class LogStatsResponse(BaseSchema):
    total_files: int
    total_size: int
    total_parsed_entries: int
    by_source_type: dict[str, int]
    by_status: dict[str, int]
    recent_uploads: int
    avg_file_size: float
    storage_used: str
