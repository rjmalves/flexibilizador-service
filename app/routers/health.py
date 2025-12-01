"""
Health check endpoints for container orchestration.

Provides liveness and readiness probes for Kubernetes/Docker health checks.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.internal.settings import Settings

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Overall health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp",
    )
    checks: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Individual component health checks",
    )


class SimpleStatus(BaseModel):
    """Simple status response for liveness/readiness probes."""

    status: str = Field(..., description="Status string")


@router.get(
    "/health",
    response_model=HealthStatus,
    summary="Health check",
    description="Check application and dependency health.",
)
async def health_check() -> HealthStatus:
    """
    Comprehensive health check.

    Returns:
        HealthStatus with component checks
    """
    checks = {}
    overall_status = "healthy"

    # S3 connectivity check (optional - don't fail if S3 not configured)
    try:
        from app.adapters.s3_repository import get_s3_repository

        _ = get_s3_repository()
        # Just verify we can get the repository instance
        checks["s3"] = {"status": "healthy"}
    except Exception as e:
        checks["s3"] = {"status": "unhealthy", "error": str(e)}
        # Don't fail overall health for S3 issues during startup

    return HealthStatus(
        status=overall_status,
        version=Settings.app_version,
        timestamp=datetime.utcnow(),
        checks=checks,
    )


@router.get(
    "/health/live",
    response_model=SimpleStatus,
    summary="Liveness probe",
    description="Simple liveness check for Kubernetes/Docker.",
)
async def liveness() -> SimpleStatus:
    """
    Simple liveness check.

    Returns 200 OK if the application is running.
    """
    return SimpleStatus(status="ok")


@router.get(
    "/health/ready",
    response_model=SimpleStatus,
    summary="Readiness probe",
    description="Readiness check - verifies application can serve requests.",
)
async def readiness() -> SimpleStatus:
    """
    Readiness check.

    Returns 200 OK if the application is ready to serve requests.
    """
    # For now, just return ready if we can process the request
    # In the future, could check S3 connectivity, etc.
    return SimpleStatus(status="ready")
