import time
import json
from datetime import datetime, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger
from app.core.config import settings


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Logs all inbound requests and outbound responses for security auditing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method

        # Skip spamming logs with frequent telemetry health checks
        is_health = path.endswith("/health")

        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start_time) * 1000)

            if not is_health:
                audit_record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "client_ip": client_ip,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
                # Write to audit log file
                audit_log_path = settings.LOGS_ROOT / "audit.log"
                settings.LOGS_ROOT.mkdir(parents=True, exist_ok=True)
                with open(audit_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(audit_record) + "\n")

            return response
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Unhandled API Exception on {method} {path}: {str(exc)}")
            raise exc
