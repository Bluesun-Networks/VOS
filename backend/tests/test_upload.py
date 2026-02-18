import pytest


@pytest.mark.asyncio
async def test_upload_raw(client):
    resp = await client.post("/api/v1/reviews/upload/raw", json={
        "content": "# My Document\n\nSome content here.",
        "title": "My Document"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "document_id" in data
    assert data["title"] == "My Document"

    # Verify document was created
    doc_resp = await client.get(f"/api/v1/documents/{data['document_id']}")
    assert doc_resp.status_code == 200
    assert doc_resp.json()["content"] == "# My Document\n\nSome content here."


@pytest.mark.asyncio
async def test_upload_raw_title_from_content(client):
    resp = await client.post("/api/v1/reviews/upload/raw", json={
        "content": "# Auto Title\n\nBody text.",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Auto Title"


@pytest.mark.asyncio
async def test_upload_file(client):
    files = {"file": ("test.md", b"# File Upload\n\nTest content.", "text/markdown")}
    resp = await client.post("/api/v1/reviews/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "document_id" in data
    assert data["title"] == "File Upload"
