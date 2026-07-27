from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        json_encoders={
            UUID: str,
            datetime: lambda dt: dt.isoformat(),
        },
    )


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: str | None = Field(default=None, description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: T | None = None
    errors: list[str] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: dict[str, Any] | None = None
    request_id: str | None = None


class AuditEntry(BaseSchema):
    action: str
    resource: str
    resource_id: str | None = None
    details: dict[str, Any] | None = None
    performed_by: str
    performed_at: datetime
    ip_address: str | None = None
