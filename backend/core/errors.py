"""Structured error handling for VOS API."""
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger("vos")


class ErrorResponse(BaseModel):
    """Standard error response returned by all API errors."""
    error: str
    detail: str
    code: Optional[str] = None


class VosError(Exception):
    """Base exception for VOS application errors."""
    def __init__(self, message: str, code: str = "internal_error", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundError(VosError):
    def __init__(self, doc_id: str):
        super().__init__(f"Document '{doc_id}' not found", code="document_not_found", status_code=404)


class ReviewNotFoundError(VosError):
    def __init__(self, review_id: str):
        super().__init__(f"Review '{review_id}' not found", code="review_not_found", status_code=404)


class PersonaNotFoundError(VosError):
    def __init__(self, persona_id: str):
        super().__init__(f"Persona '{persona_id}' not found", code="persona_not_found", status_code=404)


class LLMError(VosError):
    """Error from the LLM provider (Anthropic, etc.)."""
    def __init__(self, message: str, provider: str = "anthropic"):
        super().__init__(
            f"LLM provider error ({provider}): {message}",
            code="llm_error",
            status_code=502,
        )


class LLMAuthError(VosError):
    """Authentication error with LLM provider."""
    def __init__(self, provider: str = "anthropic"):
        super().__init__(
            f"Invalid API key for {provider}. Check your ANTHROPIC_API_KEY configuration.",
            code="llm_auth_error",
            status_code=502,
        )


class LLMRateLimitError(VosError):
    """Rate limit hit on LLM provider."""
    def __init__(self, provider: str = "anthropic"):
        super().__init__(
            f"Rate limit exceeded for {provider}. Please try again in a moment.",
            code="llm_rate_limit",
            status_code=429,
        )


class ValidationError(VosError):
    def __init__(self, message: str):
        super().__init__(message, code="validation_error", status_code=400)


def classify_anthropic_error(exc: Exception) -> VosError:
    """Convert an Anthropic SDK exception into a structured VosError."""
    exc_type = type(exc).__name__
    exc_msg = str(exc)

    if "AuthenticationError" in exc_type or "authentication" in exc_msg.lower():
        return LLMAuthError()
    if "RateLimitError" in exc_type or "rate_limit" in exc_msg.lower() or "429" in exc_msg:
        return LLMRateLimitError()
    if "APIConnectionError" in exc_type or "connection" in exc_msg.lower():
        return LLMError("Unable to connect to Anthropic API. Check network connectivity.")
    if "BadRequestError" in exc_type or "400" in exc_msg:
        return LLMError(f"Invalid request to LLM: {exc_msg}")

    return LLMError(exc_msg)


async def vos_error_handler(request: Request, exc: VosError) -> JSONResponse:
    """Handle VosError exceptions and return structured JSON."""
    logger.warning("VOS error [%s]: %s (path=%s)", exc.code, exc.message, request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.code,
            detail=exc.message,
        ).model_dump(),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected exceptions."""
    logger.error(
        "Unhandled error on %s %s: %s\n%s",
        request.method,
        request.url.path,
        str(exc),
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_error",
            detail="An unexpected error occurred. Please try again.",
        ).model_dump(),
    )
