"""Tests for test fixtures to verify setup is working."""


def test_project_root_exists(project_root):
    """Verify project root fixture returns valid path."""
    assert project_root.exists()
    assert (project_root / "main.py").exists()


def test_temp_dir_is_empty(temp_dir):
    """Verify temp_dir fixture provides empty directory."""
    assert temp_dir.exists()
    assert temp_dir.is_dir()
    assert list(temp_dir.iterdir()) == []


def test_fixtures_available(fixtures_path):
    """Verify fixtures directory exists and has expected files."""
    assert fixtures_path.exists()
    assert (fixtures_path / "deck_processado.zip").exists()
    assert (fixtures_path / "inviab_unic.rv0").exists()
    assert (fixtures_path / "relato.rv0").exists()


def test_deck_zip_exists(deck_zip_path):
    """Verify deck_zip_path fixture returns valid path."""
    assert deck_zip_path.exists()
    assert deck_zip_path.suffix == ".zip"


def test_extracted_deck_contains_files(extracted_deck):
    """Verify extracted_deck fixture extracts files correctly."""
    assert extracted_deck.exists()
    files = list(extracted_deck.iterdir())
    assert len(files) > 0
    # Should contain caso.dat
    assert (extracted_deck / "caso.dat").exists() or any(
        f.name.endswith(".dat") for f in files
    )
