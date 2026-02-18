"""Tests for observability: /ready, /metrics, version info, request logging."""
import pytest

from core.observability import metrics, _Metrics


# ---------- /ready endpoint ----------

@pytest.mark.asyncio
async def test_ready_healthy(client):
    """Readiness probe returns ready=True when DB is OK."""
    resp = await client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready"] is True


# ---------- /metrics endpoint ----------

@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Metrics endpoint returns expected structure."""
    resp = await client.get("/api/v1/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "uptime_seconds" in data
    assert "requests" in data
    assert "latency_ms" in data
    assert "reviews" in data
    assert data["requests"]["total"] >= 0
    assert "p50" in data["latency_ms"]
    assert "p95" in data["latency_ms"]


# ---------- status with versions ----------

@pytest.mark.asyncio
async def test_status_includes_versions(client):
    """Status endpoint now includes dependency version info."""
    resp = await client.get("/api/v1/status/")
    assert resp.status_code == 200
    data = resp.json()
    assert "versions" in data
    versions = data["versions"]
    assert "vos" in versions
    assert "python" in versions
    assert "fastapi" in versions
    assert "sqlalchemy" in versions
    assert "anthropic_sdk" in versions


# ---------- In-memory metrics logic ----------

class TestMetricsStore:
    def test_record_request(self):
        m = _Metrics()
        m.record_request("GET", 200, 0.05)
        m.record_request("POST", 201, 0.10)
        m.record_request("GET", 500, 0.02)
        snap = m.snapshot()
        assert snap["requests"]["total"] == 3
        assert snap["requests"]["errors_5xx"] == 1
        assert snap["requests"]["by_method"]["GET"] == 2
        assert snap["requests"]["by_status"][200] == 1

    def test_review_metrics(self):
        m = _Metrics()
        m.record_review_start()
        m.record_review_start()
        m.record_persona_completion()
        m.record_persona_completion()
        m.record_persona_completion()
        m.record_review_complete(2.5)
        m.record_review_failed()
        snap = m.snapshot()
        assert snap["reviews"]["started"] == 2
        assert snap["reviews"]["completed"] == 1
        assert snap["reviews"]["failed"] == 1
        assert snap["reviews"]["persona_completions"] == 3
        assert snap["reviews"]["avg_duration_s"] == 2.5

    def test_latency_percentiles(self):
        m = _Metrics()
        for i in range(100):
            m.record_request("GET", 200, i / 1000.0)  # 0ms to 99ms
        snap = m.snapshot()
        assert snap["latency_ms"]["p50"] > 0
        assert snap["latency_ms"]["p95"] >= snap["latency_ms"]["p50"]
        assert snap["latency_ms"]["sample_size"] == 100

    def test_empty_metrics_snapshot(self):
        m = _Metrics()
        snap = m.snapshot()
        assert snap["requests"]["total"] == 0
        assert snap["latency_ms"]["sample_size"] == 0
        assert snap["reviews"]["avg_duration_s"] == 0


# ---------- X-Request-ID header ----------

@pytest.mark.asyncio
async def test_response_has_request_id(client):
    """Every response should include an X-Request-ID header."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert "x-request-id" in resp.headers
    assert len(resp.headers["x-request-id"]) == 12
