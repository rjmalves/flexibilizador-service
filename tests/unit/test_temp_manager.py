"""Unit tests for temp directory manager."""

import pytest


class TestTempDirectory:
    """Tests for temp_directory context manager."""

    def test_temp_directory_creates_and_cleans(self, tmp_path):
        """Test temp directory is created and cleaned up."""
        from app.utils.temp_manager import temp_directory

        base_dir = str(tmp_path)
        created_path = None

        with temp_directory(base_dir=base_dir, prefix="test_") as temp_dir:
            created_path = temp_dir
            assert temp_dir.exists()
            assert temp_dir.is_dir()
            assert temp_dir.name.startswith("test_")
            # Create a file to verify cleanup
            (temp_dir / "test.txt").write_text("test content")

        # After context exits, directory should be removed
        assert not created_path.exists()

    def test_temp_directory_cleans_on_exception(self, tmp_path):
        """Test temp directory is cleaned up even on exception."""
        from app.utils.temp_manager import temp_directory

        base_dir = str(tmp_path)
        created_path = None

        with (
            pytest.raises(ValueError),
            temp_directory(base_dir=base_dir) as temp_dir,
        ):
            created_path = temp_dir
            assert temp_dir.exists()
            raise ValueError("Test exception")

        assert not created_path.exists()

    def test_temp_directory_creates_base_dir(self, tmp_path):
        """Test base directory is created if it doesn't exist."""
        from app.utils.temp_manager import temp_directory

        base_dir = tmp_path / "nested" / "base"
        assert not base_dir.exists()

        with temp_directory(base_dir=str(base_dir)) as temp_dir:
            assert base_dir.exists()
            assert temp_dir.parent == base_dir


class TestAsyncTempDirectory:
    """Tests for async_temp_directory context manager."""

    @pytest.mark.asyncio
    async def test_async_temp_directory_creates_and_cleans(self, tmp_path):
        """Test async temp directory is created and cleaned up."""
        from app.utils.temp_manager import async_temp_directory

        base_dir = str(tmp_path)
        created_path = None

        async with async_temp_directory(
            base_dir=base_dir, prefix="async_"
        ) as temp_dir:
            created_path = temp_dir
            assert temp_dir.exists()
            assert temp_dir.is_dir()
            assert temp_dir.name.startswith("async_")
            (temp_dir / "test.txt").write_text("async content")

        assert not created_path.exists()

    @pytest.mark.asyncio
    async def test_async_temp_directory_cleans_on_exception(self, tmp_path):
        """Test async temp directory is cleaned up on exception."""
        from app.utils.temp_manager import async_temp_directory

        base_dir = str(tmp_path)
        created_path = None

        with pytest.raises(RuntimeError):
            async with async_temp_directory(base_dir=base_dir) as temp_dir:
                created_path = temp_dir
                assert temp_dir.exists()
                raise RuntimeError("Async test exception")

        assert not created_path.exists()


class TestCleanupDirectory:
    """Tests for cleanup_directory function."""

    def test_cleanup_existing_directory(self, tmp_path):
        """Test cleanup of existing directory."""
        from app.utils.temp_manager import cleanup_directory

        test_dir = tmp_path / "to_cleanup"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        result = cleanup_directory(test_dir)

        assert result is True
        assert not test_dir.exists()

    def test_cleanup_nonexistent_directory(self, tmp_path):
        """Test cleanup of non-existent directory returns True."""
        from app.utils.temp_manager import cleanup_directory

        nonexistent = tmp_path / "nonexistent"
        result = cleanup_directory(nonexistent)

        assert result is True


class TestCleanupOldTempDirs:
    """Tests for cleanup_old_temp_dirs function."""

    def test_cleanup_old_directories(self, tmp_path):
        """Test cleanup of old temp directories."""
        from app.utils.temp_manager import cleanup_old_temp_dirs

        base_dir = str(tmp_path)

        # Create old directory (simulate by changing mtime)
        old_dir = tmp_path / "flex_old_123"
        old_dir.mkdir()
        (old_dir / "file.txt").write_text("old")

        # Create new directory
        new_dir = tmp_path / "flex_new_456"
        new_dir.mkdir()
        (new_dir / "file.txt").write_text("new")

        # Note: In real scenario, we'd modify mtime, but for unit test
        # we test with max_age_hours=0 to cleanup all
        removed = cleanup_old_temp_dirs(base_dir=base_dir, max_age_hours=0)

        # Both should be removed since max_age_hours=0
        assert removed >= 1

    def test_cleanup_nonexistent_base_dir(self, tmp_path):
        """Test cleanup with non-existent base directory."""
        from app.utils.temp_manager import cleanup_old_temp_dirs

        nonexistent = str(tmp_path / "nonexistent")
        removed = cleanup_old_temp_dirs(base_dir=nonexistent)

        assert removed == 0

    def test_cleanup_ignores_non_flex_dirs(self, tmp_path):
        """Test cleanup ignores directories not starting with flex_."""
        from app.utils.temp_manager import cleanup_old_temp_dirs

        base_dir = str(tmp_path)

        # Create non-flex directory
        other_dir = tmp_path / "other_dir"
        other_dir.mkdir()

        removed = cleanup_old_temp_dirs(base_dir=base_dir, max_age_hours=0)

        # other_dir should not be removed
        assert other_dir.exists()
        assert removed == 0
