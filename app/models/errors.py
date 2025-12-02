"""
Error response models for API responses.

This module defines Pydantic models for consistent error response formatting
in the API, supporting OpenAPI documentation generation.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Machine-readable error codes."""

    INVALID_REQUEST = "INVALID_REQUEST"
    ARTIFACT_NOT_FOUND = "ARTIFACT_NOT_FOUND"
    PARSE_ERROR = "PARSE_ERROR"
    NO_INFEASIBILITIES = "NO_INFEASIBILITIES"
    S3_ERROR = "S3_ERROR"
    FLEXIBILIZATION_ERROR = "FLEXIBILIZATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorResponse(BaseModel):
    """
    Standard error response format for API errors.

    All API errors return this format for consistency.
    """

    error_code: ErrorCode = Field(
        ...,
        description="Machine-readable error code",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
    details: dict[str, Any] | None = Field(
        None,
        description="Additional error context",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error_code": "ARTIFACT_NOT_FOUND",
                "message": "Could not find execution artifacts",
                "details": {
                    "bucket": "decomp-bucket",
                    "key": "artifacts/abc123/entradas/deck_processado.zip",
                },
            }
        }
    }
