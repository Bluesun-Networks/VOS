import pytest


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "VOS"
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_status_endpoint(client):
    resp = await client.get("/api/v1/status/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "unhealthy", "degraded")
    assert "checks" in data
    check_names = {c["name"] for c in data["checks"]}
    assert "database" in check_names
    # DB should always be healthy in tests
    db_check = next(c for c in data["checks"] if c["name"] == "database")
    assert db_check["status"] == "healthy"
