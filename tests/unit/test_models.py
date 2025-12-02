"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError


class TestFlexibilizationRequest:
    """Tests for FlexibilizationRequest model."""

    def test_valid_request(self):
        """Test valid request creation."""
        from app.models.flexibilizationrequest import FlexibilizationRequest

        request = FlexibilizationRequest(
            bucket="test-bucket",
            execution_hash="abc123",
            program="DECOMP",
        )

        assert request.bucket == "test-bucket"
        assert request.execution_hash == "abc123"
        assert request.program == "DECOMP"
        assert request.output_prefix == "ingest"

    def test_default_values(self):
        """Test default values are applied."""
        from app.models.flexibilizationrequest import FlexibilizationRequest

        request = FlexibilizationRequest(
            bucket="test-bucket",
            execution_hash="abc123",
        )

        assert request.program == "DECOMP"
        assert request.output_prefix == "ingest"

    def test_missing_required_field_raises_error(self):
        """Test missing required field raises ValidationError."""
        from app.models.flexibilizationrequest import FlexibilizationRequest

        with pytest.raises(ValidationError) as exc_info:
            FlexibilizationRequest(bucket="test-bucket")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("execution_hash",) for e in errors)


class TestFlexibilizationResponse:
    """Tests for FlexibilizationResponse model."""

    def test_valid_response(self):
        """Test valid response creation."""
        from app.models.flexibilizationresponse import FlexibilizationResponse

        response = FlexibilizationResponse(
            success=True,
            execution_hash="abc123",
            output_key="ingest/abc123_flexibilizado.zip",
            flexibilizations=[],
            message="No flexibilizations needed",
        )

        assert response.success is True
        assert response.execution_hash == "abc123"
        assert response.output_key == "ingest/abc123_flexibilizado.zip"
        assert response.flexibilizations == []
        assert response.message == "No flexibilizations needed"

    def test_response_with_flexibilizations(self):
        """Test response with flexibilization results."""
        from app.models.flexibilizationresponse import FlexibilizationResponse
        from app.models.flexibilizationresult import FlexibilizationResult

        result = FlexibilizationResult(
            flexType="RE",
            flexStage=1,
            flexCode=45,
            flexPatamar="MED",
            flexLimit="FOLGAINF",
            flexSubsystem="SE",
            flexAmount=100.0,
        )

        response = FlexibilizationResponse(
            success=True,
            execution_hash="abc123",
            output_key="ingest/abc123_flexibilizado.zip",
            flexibilizations=[result],
        )

        assert len(response.flexibilizations) == 1
        assert response.flexibilizations[0].flexType == "RE"


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_valid_error_response(self):
        """Test valid error response creation."""
        from app.models.errors import ErrorCode, ErrorResponse

        response = ErrorResponse(
            error_code=ErrorCode.ARTIFACT_NOT_FOUND,
            message="File not found",
            details={"bucket": "test", "key": "missing.txt"},
        )

        assert response.error_code == ErrorCode.ARTIFACT_NOT_FOUND
        assert response.message == "File not found"
        assert response.details["bucket"] == "test"

    def test_error_response_without_details(self):
        """Test error response without details."""
        from app.models.errors import ErrorCode, ErrorResponse

        response = ErrorResponse(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Something went wrong",
        )

        assert response.details is None
