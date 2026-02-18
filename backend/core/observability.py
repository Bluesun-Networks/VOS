"""Observability: request logging middleware, in-memory metrics, request IDs."""
import logging
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from threading import Lock
from typing import Optional

logger = logging.getLogger("vos.http")

# ---------------------------------------------------------------------------
# Request-scoped context  (request ID)
# ---------------------------------------------------------------------------
_request_id_ctx: dict[int, str] = {}  # task-id -> request-id


def get_request_id() -> Optional[str]:
    """Return the current request ID, if inside a request context."""
    import asyncio
    try:
        task = asyncio.current_task()
        return _request_id_ctx.get(id(task)) if task else None
    except RuntimeError:
        return None


# ---------------------------------------------------------------------------
# In-memory metrics store
# ---------------------------------------------------------------------------
class _Metrics:
    """Thread-safe in-memory metrics.  Good enough for single-process VOS."""

    def __init__(self):
        self._lock = Lock()
        self.request_count: int = 0
        self.error_count: int = 0  # 5xx responses
        self.status_counts: dict[int, int] = defaultdict(int)
        self.method_counts: dict[str, int] = defaultdict(int)
        # Latency tracking (last 1000 request durations, in seconds)
        self._latencies: list[float] = []
        self._max_latencies = 1000
        # Review metrics
        self.reviews_started: int = 0
        self.reviews_completed: int = 0
        self.reviews_failed: int = 0
        self.persona_completions: int = 0
        self._review_durations: list[float] = []
        self._started_at = time.time()

    def record_request(self, method: str, status_code: int, duration: float):
        with self._lock:
            self.request_count += 1
            self.status_counts[status_code] += 1
            self.method_counts[method] += 1
            if status_code >= 500:
                self.error_count += 1
            self._latencies.append(duration)
            if len(self._latencies) > self._max_latencies:
                self._latencies = self._latencies[-self._max_latencies:]

    def record_review_start(self):
        with self._lock:
            self.reviews_started += 1

    def record_review_complete(self, duration: float):
        with self._lock:
            self.reviews_completed += 1
            self._review_durations.append(duration)
            if len(self._review_durations) > 500:
                self._review_durations = self._review_durations[-500:]

    def record_review_failed(self):
        with self._lock:
            self.reviews_failed += 1

    def record_persona_completion(self):
        with self._lock:
            self.persona_completions += 1

    def snapshot(self) -> dict:
        with self._lock:
            latencies = sorted(self._latencies) if self._latencies else [0]
            review_durs = sorted(self._review_durations) if self._review_durations else [0]
            return {
                "uptime_seconds": round(time.time() - self._started_at, 1),
                "requests": {
                    "total": self.request_count,
                    "errors_5xx": self.error_count,
                    "by_status": dict(self.status_counts),
                    "by_method": dict(self.method_counts),
                },
                "latency_ms": {
                    "p50": round(latencies[len(latencies) // 2] * 1000, 1),
                    "p95": round(latencies[int(len(latencies) * 0.95)] * 1000, 1),
                    "p99": round(latencies[int(len(latencies) * 0.99)] * 1000, 1),
                    "sample_size": len(self._latencies),
                },
                "reviews": {
                    "started": self.reviews_started,
                    "completed": self.reviews_completed,
                    "failed": self.reviews_failed,
                    "persona_completions": self.persona_completions,
                    "avg_duration_s": round(
                        sum(self._review_durations) / len(self._review_durations), 2
                    ) if self._review_durations else 0,
                },
            }


metrics = _Metrics()


@contextmanager
def track_review():
    """Context manager to time a full review and record start/complete/fail."""
    metrics.record_review_start()
    start = time.time()
    try:
        yield
        metrics.record_review_complete(time.time() - start)
    except Exception:
        metrics.record_review_failed()
        raise


# ---------------------------------------------------------------------------
# Pure ASGI request logging middleware (does NOT buffer StreamingResponse)
# ---------------------------------------------------------------------------
_QUIET_PATHS = frozenset({"/health", "/", "/docs", "/openapi.json", "/redoc"})


class RequestLoggingMiddleware:
    """Pure ASGI middleware — logs requests without buffering response bodies.

    Unlike BaseHTTPMiddleware, this passes through StreamingResponse (SSE)
    without buffering, so events are delivered to the client in real time.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex[:12]
        method = scope.get("method", "?")
        path = scope.get("path", "/")
        start = time.time()
        status_code = 0

        # Stash request ID for downstream code
        import asyncio
        task = asyncio.current_task()
        if task:
            _request_id_ctx[id(task)] = request_id

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                # Inject X-Request-ID header
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message = {**message, "headers": headers}
            elif message["type"] == "http.response.body":
                # Only log + record metrics when the response is done
                if not message.get("more_body", False):
                    duration = time.time() - start
                    metrics.record_request(method, status_code, duration)
                    level = logging.DEBUG if path in _QUIET_PATHS else logging.INFO
                    logger.log(
                        level,
                        "%s %s %d %.0fms [%s]",
                        method,
                        path,
                        status_code,
                        duration * 1000,
                        request_id,
                    )
                    if task:
                        _request_id_ctx.pop(id(task), None)
            await send(message)

        await self.app(scope, receive, send_wrapper)
