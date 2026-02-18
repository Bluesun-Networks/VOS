import pytest


@pytest.mark.asyncio
async def test_list_reviews_empty(client):
    # Create a document first
    doc_resp = await client.post("/api/v1/documents/", json={
        "title": "Test", "content": "content"
    })
    doc_id = doc_resp.json()["id"]

    resp = await client.get(f"/api/v1/reviews/{doc_id}/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_reviews_for_nonexistent_doc(client):
    resp = await client.get("/api/v1/reviews/nonexistent/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_latest_comments_empty(client):
    doc_resp = await client.post("/api/v1/documents/", json={
        "title": "Test", "content": "content"
    })
    doc_id = doc_resp.json()["id"]

    resp = await client.get(f"/api/v1/reviews/{doc_id}/reviews/latest/comments")
    # Should return empty or 404 when no reviews exist
    assert resp.status_code in [200, 404]
