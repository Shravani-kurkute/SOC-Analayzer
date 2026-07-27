from typing import Any

from fastapi import HTTPException, status


class SentinelAIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


class AuthenticationError(SentinelAIException):
    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR",
        )


class AuthorizationError(SentinelAIException):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN",
        )


class NotFoundError(SentinelAIException):
    def __init__(self, resource: str, identifier: str | int | None = None) -> None:
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class ValidationError(SentinelAIException):
    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class ConflictError(SentinelAIException):
    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
        )


class RateLimitError(SentinelAIException):
    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT",
        )


class ServiceUnavailableError(SentinelAIException):
    def __init__(self, service: str = "Service") -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} is temporarily unavailable",
            error_code="SERVICE_UNAVAILABLE",
        )
