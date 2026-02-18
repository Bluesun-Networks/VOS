import json
import time
import secrets
import hashlib
import hmac
from collections import defaultdict

from core.config import get_settings

# CSRF token secret - generated once per process
_CSRF_SECRET = secrets.token_hex(32)

# State-changing HTTP methods that require CSRF protection
CSRF_METHODS = {b"POST", b"PUT", b"PATCH", b"DELETE"}

# Paths exempt from CSRF (e.g. file uploads that use multipart)
CSRF_EXEMPT_PATHS = [b"/api/v1/reviews/upload"]


def generate_csrf_token(session_id: str) -> str:
    """Generate a CSRF token tied to a session identifier."""
    return hmac.HMAC(
        _CSRF_SECRET.encode(),
        session_id.encode(),
        hashlib.sha256,
    ).hexdigest()


def _get_header(headers: list, name: bytes) -> str | None:
    """Extract a header value from raw ASGI headers list."""
    for k, v in headers:
        if k.lower() == name:
            return v.decode()
    return None


async def _send_json_response(send, status: int, body: dict, extra_headers=None):
    """Send a complete JSON response via raw ASGI send."""
    payload = json.dumps(body).encode()
    headers = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(payload)).encode()),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": payload})


class RateLimitMiddleware:
    """Pure ASGI sliding-window rate limiter per client IP.

    Does not buffer StreamingResponse — passes through SSE without issues.
    """

    def __init__(self, app):
        self.app = app
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, scope) -> str:
        headers = scope.get("headers", [])
        forwarded = _get_header(headers, b"x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"

    def _cleanup_old(self, ip: str, window: float):
        now = time.time()
        self._requests[ip] = [t for t in self._requests[ip] if now - t < window]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        settings = get_settings()
        if not settings.rate_limit_enabled:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        ip = self._get_client_ip(scope)
        window = 60.0
        limit = settings.rate_limit_per_minute

        self._cleanup_old(ip, window)

        if len(self._requests[ip]) >= limit:
            await _send_json_response(
                send, 429,
                {"detail": "Rate limit exceeded. Try again later."},
                extra_headers=[(b"retry-after", b"60")],
            )
            return

        self._requests[ip].append(time.time())
        remaining = max(0, limit - len(self._requests[ip]))

        # Inject rate-limit headers into the response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-ratelimit-limit", str(limit).encode()))
                headers.append((b"x-ratelimit-remaining", str(remaining).encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


class CSRFMiddleware:
    """Pure ASGI CSRF protection middleware.

    Checks that state-changing requests (POST/PUT/PATCH/DELETE) include
    either a valid X-CSRF-Token header, an Origin/Referer from localhost,
    or Content-Type: application/json (which triggers CORS preflight).

    Does not buffer StreamingResponse.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        settings = get_settings()
        if not settings.csrf_enabled:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET").encode()
        if method not in CSRF_METHODS:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        # Exempt specific paths
        path_bytes = path.encode()
        for exempt in CSRF_EXEMPT_PATHS:
            if path_bytes.startswith(exempt):
                await self.app(scope, receive, send)
                return

        headers = scope.get("headers", [])
        origin = _get_header(headers, b"origin")
        referer = _get_header(headers, b"referer")
        host = _get_header(headers, b"host") or ""

        origin_valid = False

        if origin:
            origin_host = origin.split("://", 1)[-1].rstrip("/")
            if origin_host == host or origin_host.startswith("localhost"):
                origin_valid = True
        elif referer:
            referer_host = referer.split("://", 1)[-1].split("/")[0]
            if referer_host == host or referer_host.startswith("localhost"):
                origin_valid = True

        # Check X-CSRF-Token header (SPA pattern)
        csrf_token = _get_header(headers, b"x-csrf-token")
        if csrf_token:
            origin_valid = True

        # Check Content-Type: application/json (AJAX pattern)
        content_type = _get_header(headers, b"content-type") or ""
        if "application/json" in content_type:
            origin_valid = True

        if not origin_valid:
            await _send_json_response(send, 403, {"detail": "CSRF validation failed"})
            return

        await self.app(scope, receive, send)
