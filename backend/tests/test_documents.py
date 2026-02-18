import pytest


@pytest.mark.asyncio
async def test_create_document(client):
    resp = await client.post("/api/v1/documents/", json={
        "title": "Test Doc",
        "content": "# Hello\n\nThis is a test document.",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Doc"
    assert data["content"] == "# Hello\n\nThis is a test document."
    assert data["is_archived"] is False
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    resp = await client.get("/api/v1/documents/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_documents(client):
    await client.post("/api/v1/documents/", json={
        "title": "Doc 1", "content": "content 1"
    })
    await client.post("/api/v1/documents/", json={
        "title": "Doc 2", "content": "content 2"
    })
    resp = await client.get("/api/v1/documents/")
    assert resp.status_code == 200
    docs = resp.json()
    assert len(docs) == 2


@pytest.mark.asyncio
async def test_get_document(client):
    create_resp = await client.post("/api/v1/documents/", json={
        "title": "My Doc", "content": "body text"
    })
    doc_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "My Doc"


@pytest.mark.asyncio
async def test_get_document_not_found(client):
    resp = await client.get("/api/v1/documents/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_document_content(client):
    create_resp = await client.post("/api/v1/documents/", json={
        "title": "Content Test", "content": "the content"
    })
    doc_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/documents/{doc_id}/content")
    assert resp.status_code == 200
    assert resp.json()["content"] == "the content"


@pytest.mark.asyncio
async def test_archive_and_restore(client):
    create_resp = await client.post("/api/v1/documents/", json={
        "title": "Archive Test", "content": "content"
    })
    doc_id = create_resp.json()["id"]

    csrf = {"X-CSRF-Token": "test"}

    # Archive
    resp = await client.post(f"/api/v1/documents/{doc_id}/archive", headers=csrf)
    assert resp.status_code == 200
    assert resp.json()["is_archived"] is True

    # Should not appear in default list
    list_resp = await client.get("/api/v1/documents/")
    assert all(d["id"] != doc_id for d in list_resp.json())

    # Should appear with include_archived
    list_resp = await client.get("/api/v1/documents/?include_archived=true")
    assert any(d["id"] == doc_id for d in list_resp.json())

    # Restore
    resp = await client.post(f"/api/v1/documents/{doc_id}/restore", headers=csrf)
    assert resp.status_code == 200
    assert resp.json()["is_archived"] is False


@pytest.mark.asyncio
async def test_delete_document(client):
    create_resp = await client.post("/api/v1/documents/", json={
        "title": "Delete Me", "content": "bye"
    })
    doc_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/documents/{doc_id}", headers={"X-CSRF-Token": "test"})
    assert resp.status_code == 200

    # Verify deleted
    resp = await client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 404
