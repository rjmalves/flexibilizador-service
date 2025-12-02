"""Unit tests for Flex router endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestFlexRouter:
    """Tests for /flex/ endpoint."""

    @pytest.mark.asyncio
    async def test_flex_endpoint_requires_bucket(self, async_client):
        """Test validation error when bucket is missing."""
        response = await async_client.post(
            "/flex/",
            json={"execution_hash": "test123", "program": "DECOMP"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_flex_endpoint_requires_execution_hash(self, async_client):
        """Test validation error when execution_hash is missing."""
        response = await async_client.post(
            "/flex/",
            json={"bucket": "test-bucket", "program": "DECOMP"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_flex_endpoint_success(self, async_client):
        """Test successful flexibilization request."""
        with (
            patch("app.routers.flex.get_s3_repository") as mock_get_repo,
            patch("app.routers.flex.S3UnitOfWork") as mock_uow_class,
            patch("app.routers.flex.flex_factory") as mock_factory,
        ):
            # Setup mocks
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            mock_uow = AsyncMock()
            mock_uow.output_key = "ingest/test123_flexibilizado.zip"
            mock_uow.__aenter__.return_value = mock_uow
            mock_uow.__aexit__.return_value = None
            mock_uow_class.return_value = mock_uow

            mock_flex_repo = MagicMock()
            mock_flex_repo.flex = AsyncMock(return_value=[])
            mock_factory.return_value = mock_flex_repo

            response = await async_client.post(
                "/flex/",
                json={
                    "bucket": "test-bucket",
                    "execution_hash": "test123",
                    "program": "DECOMP",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["execution_hash"] == "test123"
            assert data["output_key"] == "ingest/test123_flexibilizado.zip"

    @pytest.mark.asyncio
    async def test_flex_endpoint_artifact_not_found(self, async_client):
        """Test 404 response when artifact is not found."""
        from app.internal.exceptions import ArtifactNotFoundError

        with (
            patch("app.routers.flex.get_s3_repository") as mock_get_repo,
            patch("app.routers.flex.S3UnitOfWork") as mock_uow_class,
        ):
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            mock_uow = AsyncMock()
            mock_uow.__aenter__.side_effect = ArtifactNotFoundError(
                "Not found",
                {"bucket": "test-bucket", "key": "missing"},
            )
            mock_uow_class.return_value = mock_uow

            response = await async_client.post(
                "/flex/",
                json={
                    "bucket": "test-bucket",
                    "execution_hash": "test123",
                    "program": "DECOMP",
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["error_code"] == "ARTIFACT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_flex_endpoint_parse_error(self, async_client):
        """Test 422 response when parsing fails."""
        from app.internal.exceptions import ParseError

        with (
            patch("app.routers.flex.get_s3_repository") as mock_get_repo,
            patch("app.routers.flex.S3UnitOfWork") as mock_uow_class,
        ):
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            mock_uow = AsyncMock()
            mock_uow.__aenter__.side_effect = ParseError(
                "Invalid file format",
                {"file": "dadger.rv0"},
            )
            mock_uow_class.return_value = mock_uow

            response = await async_client.post(
                "/flex/",
                json={
                    "bucket": "test-bucket",
                    "execution_hash": "test123",
                    "program": "DECOMP",
                },
            )

            assert response.status_code == 422
            data = response.json()
            assert data["detail"]["error_code"] == "PARSE_ERROR"

    @pytest.mark.asyncio
    async def test_flex_endpoint_no_infeasibilities(self, async_client):
        """Test 422 response when no infeasibilities found."""
        from app.internal.exceptions import NoInfeasibilitiesError

        with (
            patch("app.routers.flex.get_s3_repository") as mock_get_repo,
            patch("app.routers.flex.S3UnitOfWork") as mock_uow_class,
        ):
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            mock_uow = AsyncMock()
            mock_uow.__aenter__.side_effect = NoInfeasibilitiesError(
                "No infeasibilities found",
                {"execution_hash": "test123"},
            )
            mock_uow_class.return_value = mock_uow

            response = await async_client.post(
                "/flex/",
                json={
                    "bucket": "test-bucket",
                    "execution_hash": "test123",
                    "program": "DECOMP",
                },
            )

            assert response.status_code == 422
            data = response.json()
            assert data["detail"]["error_code"] == "NO_INFEASIBILITIES"

    @pytest.mark.asyncio
    async def test_flex_endpoint_internal_error(self, async_client):
        """Test 500 response for unexpected errors."""
        with (
            patch("app.routers.flex.get_s3_repository") as mock_get_repo,
            patch("app.routers.flex.S3UnitOfWork") as mock_uow_class,
        ):
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            mock_uow = AsyncMock()
            mock_uow.__aenter__.side_effect = RuntimeError("Unexpected error")
            mock_uow_class.return_value = mock_uow

            response = await async_client.post(
                "/flex/",
                json={
                    "bucket": "test-bucket",
                    "execution_hash": "test123",
                    "program": "DECOMP",
                },
            )

            assert response.status_code == 500
            data = response.json()
            assert data["detail"]["error_code"] == "INTERNAL_ERROR"

    @pytest.mark.asyncio
    async def test_flex_endpoint_with_custom_output_prefix(self, async_client):
        """Test flexibilization with custom output prefix."""
        with (
            patch("app.routers.flex.get_s3_repository") as mock_get_repo,
            patch("app.routers.flex.S3UnitOfWork") as mock_uow_class,
            patch("app.routers.flex.flex_factory") as mock_factory,
        ):
            mock_repo = MagicMock()
            mock_get_repo.return_value = mock_repo

            mock_uow = AsyncMock()
            mock_uow.output_key = "custom/test123_flexibilizado.zip"
            mock_uow.__aenter__.return_value = mock_uow
            mock_uow.__aexit__.return_value = None
            mock_uow_class.return_value = mock_uow

            mock_flex_repo = MagicMock()
            mock_flex_repo.flex = AsyncMock(return_value=[])
            mock_factory.return_value = mock_flex_repo

            response = await async_client.post(
                "/flex/",
                json={
                    "bucket": "test-bucket",
                    "execution_hash": "test123",
                    "program": "DECOMP",
                    "output_prefix": "custom",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "custom" in data["output_key"]
