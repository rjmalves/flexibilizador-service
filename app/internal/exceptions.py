"""
Custom exceptions for the flexibilizador service.

This module defines a consistent exception hierarchy that maps to HTTP status
codes and provides structured error responses for the API.
"""

from typing import Any


class FlexibilizadorException(Exception):
    """
    Base exception for all flexibilizador service errors.

    Attributes:
        error_code: Machine-readable error code for API responses
        message: Human-readable error message
        details: Additional context about the error

    Example:
        >>> raise FlexibilizadorException("Something went wrong", {"key": "value"})
    """

    error_code: str = "INTERNAL_ERROR"
    http_status: int = 500

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to API response format."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details if self.details else None,
        }


class S3OperationError(FlexibilizadorException):
    """
    Raised when an S3 operation fails.

    Examples:
        - Upload failure
        - Permission denied
        - Network timeout

    Example:
        >>> raise S3OperationError(
        ...     "Failed to upload file",
        ...     {"bucket": "my-bucket", "key": "path/to/file"}
        ... )
    """

    error_code = "S3_ERROR"
    http_status = 500


class ArtifactNotFoundError(FlexibilizadorException):
    """
    Raised when a required S3 artifact is not found.

    Examples:
        - deck_processado.zip missing
        - inviab_unic file missing
        - relato file missing

    Example:
        >>> raise ArtifactNotFoundError(
        ...     "Object not found: s3://bucket/key",
        ...     {"bucket": "decomp-bucket", "key": "artifacts/abc/file.zip"}
        ... )
    """

    error_code = "ARTIFACT_NOT_FOUND"
    http_status = 404


class ParseError(FlexibilizadorException):
    """
    Raised when a DECOMP file cannot be parsed.

    Examples:
        - Invalid file format
        - Missing required sections
        - Encoding issues

    Example:
        >>> raise ParseError(
        ...     "Failed to parse dadger.rv0",
        ...     {"file": "dadger.rv0", "reason": "Invalid format"}
        ... )
    """

    error_code = "PARSE_ERROR"
    http_status = 422


class FlexibilizationError(FlexibilizadorException):
    """
    Raised when flexibilization processing fails.

    Examples:
        - Invalid constraint type
        - Processing logic error

    Example:
        >>> raise FlexibilizationError(
        ...     "Failed to apply flexibilization",
        ...     {"constraint": "RE", "reason": "Unknown constraint type"}
        ... )
    """

    error_code = "FLEXIBILIZATION_ERROR"
    http_status = 500


class NoInfeasibilitiesError(FlexibilizadorException):
    """
    Raised when no infeasibilities are found to process.

    This is not necessarily an error - it may indicate the model is already
    feasible.

    Example:
        >>> raise NoInfeasibilitiesError(
        ...     "No infeasibilities found in execution",
        ...     {"execution_hash": "abc123"}
        ... )
    """

    error_code = "NO_INFEASIBILITIES"
    http_status = 422


class ValidationError(FlexibilizadorException):
    """
    Raised when request validation fails beyond Pydantic checks.

    Example:
        >>> raise ValidationError(
        ...     "Invalid execution hash format",
        ...     {"execution_hash": "invalid!", "expected": "alphanumeric"}
        ... )
    """

    error_code = "INVALID_REQUEST"
    http_status = 400
