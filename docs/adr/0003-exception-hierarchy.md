# ADR-0003: Custom Exception Hierarchy

## Status

Accepted

## Context

The original service had inconsistent error handling:
- Some errors returned raw Python exceptions
- HTTP status codes were not always appropriate
- Error messages varied in format and detail
- Clients couldn't programmatically identify error types

We needed a consistent approach to error handling that:
1. Provides meaningful error messages
2. Uses appropriate HTTP status codes
3. Allows clients to identify error types programmatically
4. Supports error details for debugging

## Decision

Implement a custom exception hierarchy with:

1. **Base exception class** (`FlexibilizadorError`) with error code, message, and details
2. **Specific exception classes** for different error categories
3. **FastAPI exception handler** to convert exceptions to JSON responses
4. **Consistent error response format** (`ErrorResponse` model)

### Exception Hierarchy

```python
class FlexibilizadorError(Exception):
    """Base exception with error code and HTTP status."""
    error_code: str
    status_code: int
    message: str
    details: dict

class InvalidRequestError(FlexibilizadorError):
    """Invalid request parameters (400)"""

class ArtifactNotFoundError(FlexibilizadorError):
    """S3 artifacts not found (404)"""

class ParseError(FlexibilizadorError):
    """Failed to parse DECOMP files (422)"""

class S3Error(FlexibilizadorError):
    """S3 operation failed (500)"""

class FlexibilizationError(FlexibilizadorError):
    """Internal processing error (500)"""
```

### Error Response Format

```json
{
  "error": "ARTIFACT_NOT_FOUND",
  "message": "Required S3 objects not found",
  "details": {
    "bucket": "decomp-bucket",
    "missing_keys": ["artifacts/abc/entradas/deck_processado.zip"]
  }
}
```

### Exception Handler Registration

```python
@app.exception_handler(FlexibilizadorError)
async def flexibilizador_error_handler(request: Request, exc: FlexibilizadorError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            details=exc.details,
        ).model_dump(),
    )
```

## Consequences

### Positive

- **Consistent API**: All errors follow the same format
- **Programmatic handling**: Clients can switch on `error` field
- **Appropriate status codes**: HTTP semantics are respected
- **Debugging support**: `details` field provides context
- **Type safety**: Exception classes catch errors at development time

### Negative

- **Boilerplate**: Each error type requires a class definition
- **Learning curve**: Developers must use correct exception types
- **Maintenance**: New error types require new classes

### Neutral

- Error codes use SCREAMING_SNAKE_CASE convention
- Details field is optional (empty dict if not provided)
- Stack traces logged server-side, not exposed to clients

## Error Code Reference

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Missing or invalid request parameters |
| `ARTIFACT_NOT_FOUND` | 404 | S3 objects not found |
| `PARSE_ERROR` | 422 | Failed to parse DECOMP files |
| `S3_ERROR` | 500 | S3 operation failed |
| `FLEXIBILIZATION_ERROR` | 500 | Internal processing error |
