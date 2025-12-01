"""
Shared test fixtures for flexibilizador-service tests.

This module provides fixtures for:
- Temporary directories
- Mocked S3 with moto
- Example DECOMP artifacts from tests/fixtures/mocks
"""

import os
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

# =============================================================================
# Logger Configuration (autouse - runs for all tests)
# =============================================================================


@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logger for tests."""
    from app.utils.log import Log

    if Log.LOGGER is None:
        Log.configure_logging("")
    yield


# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


# =============================================================================
# AWS/S3 Fixtures (moto-based)
# =============================================================================


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    yield
    # Cleanup
    for key in [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SECURITY_TOKEN",
        "AWS_SESSION_TOKEN",
    ]:
        os.environ.pop(key, None)


@pytest.fixture
def s3_client(aws_credentials):
    """Provide a moto-mocked S3 client."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        yield client


@pytest.fixture
def s3_bucket(s3_client):
    """Create a test bucket and return its name."""
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    return bucket_name


@pytest.fixture
def s3_repo(aws_credentials):
    """Provide a mocked S3Repository."""
    from app.adapters.s3_repository import S3Repository, reset_s3_repository

    with mock_aws():
        # Create bucket first
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")

        repo = S3Repository(region="us-east-1")
        yield repo

        repo.close()
        reset_s3_repository()


# =============================================================================
# Test Fixtures (Mock DECOMP files)
# =============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mocks"


@pytest.fixture
def fixtures_path():
    """Return path to test fixtures directory."""
    if not FIXTURES_DIR.exists():
        pytest.skip("Test fixtures not available")
    return FIXTURES_DIR


@pytest.fixture
def deck_zip_path(fixtures_path):
    """Return path to deck_processado.zip."""
    path = fixtures_path / "deck_processado.zip"
    if not path.exists():
        pytest.skip("deck_processado.zip not available")
    return path


@pytest.fixture
def inviab_unic_path(fixtures_path):
    """Return path to inviab_unic.rv0."""
    path = fixtures_path / "inviab_unic.rv0"
    if not path.exists():
        pytest.skip("inviab_unic.rv0 not available")
    return path


@pytest.fixture
def relato_path(fixtures_path):
    """Return path to relato.rv0."""
    path = fixtures_path / "relato.rv0"
    if not path.exists():
        pytest.skip("relato.rv0 not available")
    return path


@pytest.fixture
def dadger_path(fixtures_path):
    """Return path to dadger.rv0."""
    path = fixtures_path / "dadger.rv0"
    if not path.exists():
        pytest.skip("dadger.rv0 not available")
    return path


@pytest.fixture
def extracted_deck(deck_zip_path, temp_dir):
    """Extract deck_processado.zip to temp directory."""
    from app.utils.zip_utils import extract_zip

    extract_zip(deck_zip_path, temp_dir)
    return temp_dir


@pytest.fixture
def s3_with_artifacts(
    aws_credentials, deck_zip_path, inviab_unic_path, relato_path
):
    """Upload all required artifacts to mocked S3."""
    with mock_aws():
        bucket_name = "test-bucket"
        execution_hash = "test123"

        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=bucket_name)

        # Upload deck
        deck_key = f"artifacts/{execution_hash}/entradas/deck_processado.zip"
        client.upload_file(str(deck_zip_path), bucket_name, deck_key)

        # Upload inviab_unic
        inviab_key = f"artifacts/{execution_hash}/saidas/inviab_unic.rv0"
        client.upload_file(str(inviab_unic_path), bucket_name, inviab_key)

        # Upload relato
        relato_key = f"artifacts/{execution_hash}/saidas/relato.rv0"
        client.upload_file(str(relato_path), bucket_name, relato_key)

        yield {
            "bucket": bucket_name,
            "execution_hash": execution_hash,
            "deck_key": deck_key,
            "inviab_key": inviab_key,
            "relato_key": relato_key,
            "client": client,
        }


# =============================================================================
# Application Fixtures
# =============================================================================


@pytest.fixture
def app():
    """Create test FastAPI application."""
    from main import app

    return app


@pytest.fixture
async def async_client(app):
    """Create async test client for API testing."""
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
