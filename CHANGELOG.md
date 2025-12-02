# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-01

### Added

- **S3 Integration**: Full S3 support for artifact storage

  - `S3Repository` for async S3 operations using boto3 with ThreadPoolExecutor
  - `S3UnitOfWork` for coordinating download → process → upload workflows
  - Support for custom S3 endpoints (MinIO, LocalStack)

- **Health Endpoints**: Kubernetes/Docker-compatible health checks

  - `GET /health` - Comprehensive health status with version info
  - `GET /health/live` - Liveness probe
  - `GET /health/ready` - Readiness probe with dependency checks

- **Error Handling**: Consistent error response format

  - Custom exception hierarchy (`FlexibilizadorError`, `ArtifactNotFoundError`, etc.)
  - `ErrorResponse` model for structured error responses
  - Error codes for programmatic error handling

- **Utilities**:

  - `zip_utils.py` - Zip extraction and creation utilities
  - `temp_manager.py` - Temporary directory lifecycle management

- **Docker Support**:

  - Multi-stage Dockerfile for optimized image size
  - Docker Compose configuration with Traefik labels
  - systemd service unit for production deployment
  - Non-root container execution

- **Documentation**:

  - Complete README with quickstart and API reference
  - Migration guide from v1.x to v2.0
  - Deployment guide with Docker and systemd instructions
  - Architecture Decision Records (ADRs)
  - API examples (Python and curl)

- **Testing**:
  - Comprehensive test suite using moto for S3 mocking
  - Unit tests for all new components
  - Integration tests for health endpoints

### Changed

- **BREAKING**: Request format changed

  - Old: `{"id": "<base62_encoded_path>"}`
  - New: `{"bucket": "...", "execution_hash": "...", "program": "DECOMP"}`

- **BREAKING**: Response format changed

  - Now includes `success`, `output_key`, and `flexibilizations` fields
  - Structured `ErrorResponse` for all errors

- **BREAKING**: Default port changed from 80 to 8000

- Logging now uses structured JSON format for better observability
- Settings managed via pydantic-settings with environment variables

### Removed

- **BREAKING**: base62 path encoding removed
- **BREAKING**: Filesystem-based storage removed
- `pybase62` dependency removed
- `uriparserrepository` module removed

### Security

- Non-root container execution
- IAM-based authentication for S3 (no hardcoded credentials)
- Input validation on all request parameters

### Migration

See [MIGRATION.md](docs/MIGRATION.md) for detailed upgrade instructions.

## [1.x.x] - Previous Versions

Previous versions used filesystem-based storage with base62-encoded paths.
These versions are not documented in this changelog.

---

## Release Checklist

When releasing a new version:

1. Update version in `app/internal/settings.py`
2. Update this CHANGELOG
3. Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push tag: `git push origin vX.Y.Z`
5. Build Docker image: `docker build -t flexibilizador-service:X.Y.Z .`
