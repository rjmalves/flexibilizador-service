"""Unit tests for zip utilities."""

import zipfile

import pytest


class TestExtractZip:
    """Tests for extract_zip function."""

    def test_extract_zip_success(self, deck_zip_path, temp_dir):
        """Test successful zip extraction."""
        from app.utils.zip_utils import extract_zip

        # Act
        extract_zip(deck_zip_path, temp_dir)

        # Assert
        files = list(temp_dir.iterdir())
        assert len(files) > 0

    def test_extract_zip_invalid_raises_error(self, temp_dir):
        """Test extracting invalid zip raises BadZipFile."""
        from app.utils.zip_utils import extract_zip

        # Arrange
        invalid_zip = temp_dir / "invalid.zip"
        invalid_zip.write_text("not a zip file")

        # Act & Assert
        with pytest.raises(zipfile.BadZipFile):
            extract_zip(invalid_zip, temp_dir / "output")


class TestCreateZip:
    """Tests for create_zip function."""

    def test_create_zip_success(self, temp_dir):
        """Test successful zip creation."""
        from app.utils.zip_utils import create_zip

        # Arrange
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        zip_path = temp_dir / "output.zip"

        # Act
        create_zip(source_dir, zip_path)

        # Assert
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            assert "file1.txt" in names
            assert "file2.txt" in names

    def test_create_zip_empty_directory_raises_error(self, temp_dir):
        """Test creating zip from empty directory raises ValueError."""
        from app.utils.zip_utils import create_zip

        # Arrange
        source_dir = temp_dir / "empty"
        source_dir.mkdir()
        zip_path = temp_dir / "output.zip"

        # Act & Assert
        with pytest.raises(ValueError, match="empty"):
            create_zip(source_dir, zip_path)

    def test_create_zip_nonexistent_directory_raises_error(self, temp_dir):
        """Test creating zip from nonexistent directory raises FileNotFoundError."""
        from app.utils.zip_utils import create_zip

        # Arrange
        source_dir = temp_dir / "nonexistent"
        zip_path = temp_dir / "output.zip"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            create_zip(source_dir, zip_path)


class TestGetZipFileList:
    """Tests for get_zip_file_list function."""

    def test_get_zip_file_list(self, deck_zip_path):
        """Test getting list of files in zip."""
        from app.utils.zip_utils import get_zip_file_list

        # Act
        files = get_zip_file_list(deck_zip_path)

        # Assert
        assert len(files) > 0
        assert isinstance(files, list)
        assert all(isinstance(f, str) for f in files)
