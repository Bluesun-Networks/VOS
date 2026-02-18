"""Tests for error handling: structured responses, classification, and edge cases."""
import pytest

from core.errors import (
    VosError,
    DocumentNotFoundError,
    ReviewNotFoundError,
    PersonaNotFoundError,
    LLMError,
    LLMAuthError,
    LLMRateLimitError,
    ValidationError,
    classify_anthropic_error,
)


# ---------- classify_anthropic_error ----------

class TestClassifyAnthropicError:
    def test_authentication_error_by_type_name(self):
        """AuthenticationError class name maps to LLMAuthError."""
        exc = type("AuthenticationError", (Exception,), {})("invalid key")
        result = classify_anthropic_error(exc)
        assert isinstance(result, LLMAuthError)
        assert result.code == "llm_auth_error"
        assert result.status_code == 502

    def test_authentication_error_by_message(self):
        """Exception with 'authentication' in message maps to LLMAuthError."""
        result = classify_anthropic_error(Exception("authentication failed for key"))
        assert isinstance(result, LLMAuthError)

    def test_rate_limit_error_by_type_name(self):
        exc = type("RateLimitError", (Exception,), {})("too many requests")
        result = classify_anthropic_error(exc)
        assert isinstance(result, LLMRateLimitError)
        assert result.code == "llm_rate_limit"
        assert result.status_code == 429

    def test_rate_limit_error_by_message(self):
        result = classify_anthropic_error(Exception("rate_limit exceeded"))
        assert isinstance(result, LLMRateLimitError)

    def test_rate_limit_error_by_status_code(self):
        result = classify_anthropic_error(Exception("Error 429: too many requests"))
        assert isinstance(result, LLMRateLimitError)

    def test_connection_error_by_type_name(self):
        exc = type("APIConnectionError", (Exception,), {})("timeout")
        result = classify_anthropic_error(exc)
        assert isinstance(result, LLMError)
        assert "connect" in result.message.lower()

    def test_connection_error_by_message(self):
        result = classify_anthropic_error(Exception("connection refused"))
        assert isinstance(result, LLMError)
        assert "connect" in result.message.lower()

    def test_bad_request_error(self):
        exc = type("BadRequestError", (Exception,), {})("invalid model")
        result = classify_anthropic_error(exc)
        assert isinstance(result, LLMError)
        assert "invalid request" in result.message.lower()

    def test_generic_error_fallback(self):
        result = classify_anthropic_error(Exception("something unexpected"))
        assert isinstance(result, LLMError)
        assert result.code == "llm_error"
        assert "something unexpected" in result.message


# ---------- VosError hierarchy ----------

class TestVosErrorHierarchy:
    def test_document_not_found(self):
        err = DocumentNotFoundError("abc123")
        assert err.status_code == 404
        assert err.code == "document_not_found"
        assert "abc123" in err.message

    def test_review_not_found(self):
        err = ReviewNotFoundError("rev-1")
        assert err.status_code == 404
        assert err.code == "review_not_found"

    def test_persona_not_found(self):
        err = PersonaNotFoundError("p-x")
        assert err.status_code == 404
        assert err.code == "persona_not_found"

    def test_llm_error(self):
        err = LLMError("overloaded")
        assert err.status_code == 502
        assert err.code == "llm_error"

    def test_validation_error(self):
        err = ValidationError("title is required")
        assert err.status_code == 400
        assert err.code == "validation_error"

    def test_all_are_vos_errors(self):
        errors = [
            DocumentNotFoundError("x"),
            ReviewNotFoundError("x"),
            PersonaNotFoundError("x"),
            LLMError("x"),
            LLMAuthError(),
            LLMRateLimitError(),
            ValidationError("x"),
        ]
        for err in errors:
            assert isinstance(err, VosError)


# ---------- HTTP error responses ----------

@pytest.mark.asyncio
async def test_document_404_returns_json(client):
    """GET /api/v1/documents/nonexistent returns structured 404."""
    resp = await client.get("/api/v1/documents/nonexistent")
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body

@pytest.mark.asyncio
async def test_review_404_returns_json(client):
    """GET reviews for nonexistent doc returns structured error."""
    # First create a doc so we can query reviews for it
    create = await client.post("/api/v1/documents/", json={
        "title": "Err Test", "content": "body",
    })
    doc_id = create.json()["id"]

    resp = await client.get(f"/api/v1/reviews/{doc_id}/reviews/fake-review-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_empty_file_rejected(client):
    """Uploading empty content via raw endpoint returns 400."""
    resp = await client.post("/api/v1/reviews/upload/raw", json={
        "content": "   ",
        "title": "blank",
    })
    assert resp.status_code == 400
    body = resp.json()
    assert "detail" in body
    assert "empty" in body["detail"].lower()


@pytest.mark.asyncio
async def test_upload_non_md_file_rejected(client):
    """Uploading a non-.md file returns 400."""
    import io
    resp = await client.post(
        "/api/v1/reviews/upload",
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "detail" in body
    assert ".md" in body["detail"]


@pytest.mark.asyncio
async def test_archive_nonexistent_doc(client):
    """Archiving a nonexistent doc returns 404."""
    resp = await client.post(
        "/api/v1/documents/nonexistent/archive",
        headers={"X-CSRF-Token": "test"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_doc(client):
    """Deleting a nonexistent doc returns 404."""
    resp = await client.delete(
        "/api/v1/documents/nonexistent",
        headers={"X-CSRF-Token": "test"},
    )
    assert resp.status_code == 404
