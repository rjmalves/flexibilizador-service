"""Unit tests for S3 Repository."""

import pytest


class TestS3Repository:
    """Tests for S3Repository with mocked S3."""

    @pytest.mark.asyncio
    async def test_upload_and_download_file(self, s3_repo, temp_dir):
        """Test upload and download round-trip."""
        # Arrange
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello world")
        download_path = temp_dir / "downloaded.txt"

        # Act - Upload
        key = await s3_repo.upload_file(
            str(test_file), "test-bucket", "test.txt"
        )

        # Assert - Upload
        assert key == "test.txt"

        # Act - Download
        await s3_repo.download_file(
            "test-bucket", "test.txt", str(download_path)
        )

        # Assert - Download
        assert download_path.exists()
        assert download_path.read_text() == "hello world"

    @pytest.mark.asyncio
    async def test_download_bytes(self, s3_repo, temp_dir):
        """Test downloading file content as bytes."""
        # Arrange
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        await s3_repo.upload_file(str(test_file), "test-bucket", "test.txt")

        # Act
        content = await s3_repo.download_bytes("test-bucket", "test.txt")

        # Assert
        assert content == b"test content"

    @pytest.mark.asyncio
    async def test_object_exists_true(self, s3_repo, temp_dir):
        """Test object_exists returns True for existing object."""
        # Arrange
        test_file = temp_dir / "test.txt"
        test_file.write_text("exists")
        await s3_repo.upload_file(str(test_file), "test-bucket", "exists.txt")

        # Act
        exists = await s3_repo.object_exists("test-bucket", "exists.txt")

        # Assert
        assert exists is True

    @pytest.mark.asyncio
    async def test_object_exists_false(self, s3_repo):
        """Test object_exists returns False for non-existing object."""
        # Act
        exists = await s3_repo.object_exists("test-bucket", "nonexistent.txt")

        # Assert
        assert exists is False

    @pytest.mark.asyncio
    async def test_list_objects(self, s3_repo, temp_dir):
        """Test listing objects by prefix."""
        # Arrange
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        await s3_repo.upload_file(
            str(test_file), "test-bucket", "prefix/file1.txt"
        )
        await s3_repo.upload_file(
            str(test_file), "test-bucket", "prefix/file2.txt"
        )
        await s3_repo.upload_file(
            str(test_file), "test-bucket", "other/file3.txt"
        )

        # Act
        keys = await s3_repo.list_objects("test-bucket", "prefix/")

        # Assert
        assert len(keys) == 2
        assert "prefix/file1.txt" in keys
        assert "prefix/file2.txt" in keys

    @pytest.mark.asyncio
    async def test_download_nonexistent_raises_error(self, s3_repo, temp_dir):
        """Test downloading non-existent file raises ArtifactNotFoundError."""
        from app.internal.exceptions import ArtifactNotFoundError

        download_path = temp_dir / "nonexistent.txt"

        with pytest.raises(ArtifactNotFoundError) as exc_info:
            await s3_repo.download_file(
                "test-bucket", "nonexistent.txt", str(download_path)
            )

        assert "test-bucket" in exc_info.value.details["bucket"]
        assert "nonexistent.txt" in exc_info.value.details["key"]
