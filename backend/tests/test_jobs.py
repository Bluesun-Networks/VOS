import pytest


@pytest.mark.asyncio
async def test_list_jobs_empty(client):
    resp = await client.get("/api/v1/jobs/")
    assert resp.status_code == 200
    assert resp.json() == []
