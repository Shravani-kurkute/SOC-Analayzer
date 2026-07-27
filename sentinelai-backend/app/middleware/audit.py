import time
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        if request.url.path.startswith("/api/"):
            audit_log: dict[str, Any] = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": request.headers.get("x-request-id"),
            }

            if response.status_code >= 400:
                audit_log["query_params"] = dict(request.query_params)

            logger.info("audit_trail", **audit_log)

        response.headers["X-Response-Time-Ms"] = str(round(duration * 1000, 2))

        return response
