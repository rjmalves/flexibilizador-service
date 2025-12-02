"""Unit tests for custom exceptions."""

import pytest


class TestFlexibilizadorException:
    """Tests for FlexibilizadorException and subclasses."""

    def test_base_exception(self):
        """Test base FlexibilizadorException."""
        from app.internal.exceptions import FlexibilizadorException

        exc = FlexibilizadorException("Something went wrong", {"key": "value"})

        assert exc.message == "Something went wrong"
        assert exc.details == {"key": "value"}
        assert exc.error_code == "INTERNAL_ERROR"
        assert exc.http_status == 500

    def test_to_dict(self):
        """Test exception to_dict method."""
        from app.internal.exceptions import FlexibilizadorException

        exc = FlexibilizadorException("Error message", {"detail": "info"})
        result = exc.to_dict()

        assert result["error_code"] == "INTERNAL_ERROR"
        assert result["message"] == "Error message"
        assert result["details"] == {"detail": "info"}

    def test_artifact_not_found_error(self):
        """Test ArtifactNotFoundError."""
        from app.internal.exceptions import ArtifactNotFoundError

        exc = ArtifactNotFoundError(
            "Object not found",
            {"bucket": "test-bucket", "key": "missing.txt"},
        )

        assert exc.error_code == "ARTIFACT_NOT_FOUND"
        assert exc.http_status == 404
        assert "bucket" in exc.details

    def test_parse_error(self):
        """Test ParseError."""
        from app.internal.exceptions import ParseError

        exc = ParseError(
            "Failed to parse file",
            {"file": "dadger.rv0", "reason": "Invalid format"},
        )

        assert exc.error_code == "PARSE_ERROR"
        assert exc.http_status == 422

    def test_s3_operation_error(self):
        """Test S3OperationError."""
        from app.internal.exceptions import S3OperationError

        exc = S3OperationError(
            "Upload failed",
            {"bucket": "test", "error": "Access denied"},
        )

        assert exc.error_code == "S3_ERROR"
        assert exc.http_status == 500

    def test_no_infeasibilities_error(self):
        """Test NoInfeasibilitiesError."""
        from app.internal.exceptions import NoInfeasibilitiesError

        exc = NoInfeasibilitiesError(
            "No infeasibilities found",
            {"execution_hash": "abc123"},
        )

        assert exc.error_code == "NO_INFEASIBILITIES"
        assert exc.http_status == 422

    def test_validation_error(self):
        """Test ValidationError."""
        from app.internal.exceptions import ValidationError

        exc = ValidationError(
            "Invalid input",
            {"field": "execution_hash", "reason": "empty"},
        )

        assert exc.error_code == "INVALID_REQUEST"
        assert exc.http_status == 400

    def test_exception_can_be_raised(self):
        """Test exceptions can be raised and caught."""
        from app.internal.exceptions import (
            ArtifactNotFoundError,
            FlexibilizadorException,
        )

        with pytest.raises(FlexibilizadorException):
            raise ArtifactNotFoundError("Not found", {})
