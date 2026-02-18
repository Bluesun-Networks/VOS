import pytest


@pytest.mark.asyncio
async def test_list_personas(client):
    """Personas endpoint returns the 7 default personas (from hardcoded fallback or DB)."""
    resp = await client.get("/api/v1/personas/")
    assert resp.status_code == 200
    personas = resp.json()
    assert len(personas) == 7
    names = {p["name"] for p in personas}
    assert "Devil's Advocate" in names
    assert "Executive Summarizer" in names


@pytest.mark.asyncio
async def test_persona_has_required_fields(client):
    resp = await client.get("/api/v1/personas/")
    persona = resp.json()[0]
    for field in ["id", "name", "description", "system_prompt", "tone", "focus_areas", "color", "weight"]:
        assert field in persona, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_get_persona_by_id(client):
    resp = await client.get("/api/v1/personas/devils-advocate")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Devil's Advocate"


@pytest.mark.asyncio
async def test_get_persona_not_found(client):
    resp = await client.get("/api/v1/personas/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_persona_weight(client):
    resp = await client.patch("/api/v1/personas/devils-advocate", json={"weight": 2.5})
    assert resp.status_code == 200
    assert resp.json()["weight"] == 2.5


@pytest.mark.asyncio
async def test_update_persona_weight_out_of_range(client):
    resp = await client.patch("/api/v1/personas/devils-advocate", json={"weight": 10.0})
    assert resp.status_code == 400

    resp = await client.patch("/api/v1/personas/devils-advocate", json={"weight": -1.0})
    assert resp.status_code == 400
