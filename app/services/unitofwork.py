import shutil
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from os import chdir, curdir
from pathlib import Path
from typing import Any

from app.adapters.filesrepository import (
    AbstractFilesRepository,
    RawFilesRepository,
)
from app.adapters.s3_repository import AbstractS3Repository
from app.internal.exceptions import ArtifactNotFoundError
from app.internal.settings import Settings
from app.utils.log import Log
from app.utils.temp_manager import async_temp_directory
from app.utils.zip_utils import create_zip, extract_zip


class AbstractUnitOfWork(ABC):
    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def files(self) -> AbstractFilesRepository:
        raise NotImplementedError


class FSUnitOfWork(AbstractUnitOfWork):
    def __init__(self, directory: str):
        self._current_path = Path(curdir).resolve()
        self._case_directory = directory
        self._files: RawFilesRepository | None = None

    def __create_repository(self) -> None:
        if self._files is None:
            self._files = RawFilesRepository(str(self._case_directory))

    def __enter__(self) -> "FSUnitOfWork":
        chdir(self._case_directory)
        self.__create_repository()
        uow = super().__enter__()
        assert isinstance(uow, FSUnitOfWork)
        return uow

    def __exit__(self, *args: object) -> None:
        chdir(self._current_path)
        super().__exit__(*args)

    @property
    def files(self) -> RawFilesRepository:
        assert isinstance(self._files, RawFilesRepository)
        return self._files

    def rollback(self) -> None:
        pass


class S3UnitOfWork(AbstractUnitOfWork):
    """
    Unit of Work for S3-based DECOMP artifact processing.

    Coordinates:
    1. Downloading artifacts from S3
    2. Extracting zip to temp directory
    3. Providing files repository for processing
    4. Creating output zip with modified files
    5. Uploading results to S3
    6. Cleaning up temp directory

    Usage:
        async with S3UnitOfWork(s3_repo, bucket, hash) as uow:
            flex_repo.flex(rules, uow)
        # Temp dir cleaned up, results uploaded
    """

    def __init__(
        self,
        s3_repo: AbstractS3Repository,
        bucket: str,
        execution_hash: str,
        output_prefix: str = "ingest",
    ):
        """
        Initialize S3UnitOfWork.

        Args:
            s3_repo: S3 repository for downloads/uploads
            bucket: S3 bucket name
            execution_hash: Execution identifier (artifacts/<hash>/)
            output_prefix: S3 prefix for output zip (default: "ingest")
        """
        self._s3_repo = s3_repo
        self._bucket = bucket
        self._execution_hash = execution_hash
        self._output_prefix = output_prefix

        self._temp_dir: Path | None = None
        self._files: RawFilesRepository | None = None
        self._output_key: str | None = None
        self._temp_context: AbstractAsyncContextManager[Path] | None = None

    @property
    def files(self) -> RawFilesRepository:
        """Get the files repository for accessing DECOMP files."""
        if self._files is None:
            raise RuntimeError("S3UnitOfWork not entered - use 'async with'")
        return self._files

    @property
    def output_key(self) -> str | None:
        """Get the S3 key of the uploaded output zip."""
        return self._output_key

    def rollback(self):
        """Rollback not supported in async context."""
        pass

    async def __aenter__(self) -> "S3UnitOfWork":
        """
        Enter the unit of work context.

        1. Creates temp directory
        2. Downloads deck_processado.zip
        3. Downloads inviab_unic and relato files
        4. Extracts zip to temp directory
        5. Initializes files repository
        """
        Log.log().info(f"Entering S3UnitOfWork for {self._execution_hash}")

        # Create temp directory
        self._temp_context = async_temp_directory(
            base_dir=Settings.temp_dir,
            prefix=f"flex_{self._execution_hash}_",
        )
        assert self._temp_context is not None
        self._temp_dir = await self._temp_context.__aenter__()

        try:
            # Determine file extension from caso.dat or default
            extension = await self._get_file_extension()

            # Download artifacts
            await self._download_artifacts(extension)

            # Initialize files repository
            self._files = RawFilesRepository(str(self._temp_dir))

            return self

        except Exception:
            # Cleanup on failure
            if self._temp_context is not None:
                await self._temp_context.__aexit__(None, None, None)
            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """
        Exit the unit of work context.

        If no exception occurred:
        1. Creates output zip from modified files
        2. Uploads zip to S3

        Always cleans up temp directory.
        """
        try:
            if exc_type is None:
                # Success - create and upload output
                await self._upload_results()
        finally:
            # Always cleanup temp directory
            if self._temp_context:
                await self._temp_context.__aexit__(exc_type, exc_val, exc_tb)

        Log.log().info(f"Exited S3UnitOfWork for {self._execution_hash}")

    async def _get_file_extension(self) -> str:
        """
        Get the file extension for this execution.

        Tries to download caso.dat first to determine extension,
        falls back to "rv0" if not found.
        """
        assert self._temp_dir is not None, "temp_dir must be set before calling"

        deck_key = (
            f"artifacts/{self._execution_hash}/entradas/deck_processado.zip"
        )

        # Download the zip first to check caso.dat
        zip_path = self._temp_dir / "deck_processado.zip"
        await self._s3_repo.download_file(self._bucket, deck_key, str(zip_path))

        # Extract to check caso.dat
        extract_dir = self._temp_dir / "extracted"
        extract_dir.mkdir()
        extract_zip(zip_path, extract_dir)

        # Read caso.dat for extension
        caso_path = extract_dir / "caso.dat"
        if caso_path.exists():
            # caso.dat contains the file extension on first line
            content = caso_path.read_text().strip()
            extension = content.split()[0] if content else "rv0"
            Log.log().info(f"File extension from caso.dat: {extension}")
        else:
            extension = "rv0"
            Log.log().warning(
                "caso.dat not found, using default extension: rv0"
            )

        # Move extracted files to temp_dir root
        for item in extract_dir.iterdir():
            shutil.move(str(item), str(self._temp_dir / item.name))
        extract_dir.rmdir()
        zip_path.unlink()

        return extension

    async def _download_artifacts(self, extension: str) -> None:
        """
        Download output artifacts (inviab_unic, relato).

        Args:
            extension: File extension (e.g., "rv0")
        """
        assert self._temp_dir is not None, "temp_dir must be set before calling"

        # Download inviab_unic
        inviab_key = (
            f"artifacts/{self._execution_hash}/saidas/inviab_unic.{extension}"
        )
        inviab_path = self._temp_dir / f"inviab_unic.{extension}"

        try:
            await self._s3_repo.download_file(
                self._bucket, inviab_key, str(inviab_path)
            )
            Log.log().info(f"Downloaded inviab_unic.{extension}")
        except ArtifactNotFoundError:
            Log.log().warning(f"inviab_unic.{extension} not found")

        # Download relato
        relato_key = (
            f"artifacts/{self._execution_hash}/saidas/relato.{extension}"
        )
        relato_path = self._temp_dir / f"relato.{extension}"

        try:
            await self._s3_repo.download_file(
                self._bucket, relato_key, str(relato_path)
            )
            Log.log().info(f"Downloaded relato.{extension}")
        except ArtifactNotFoundError:
            Log.log().warning(f"relato.{extension} not found")

    async def _upload_results(self) -> None:
        """Create output zip and upload to S3."""
        assert self._temp_dir is not None, "temp_dir must be set before calling"

        # Create output zip
        output_zip_name = f"{self._execution_hash}_flexibilizado.zip"
        output_zip_path = self._temp_dir.parent / output_zip_name

        create_zip(
            self._temp_dir,
            output_zip_path,
            compression_level=Settings.zip_compression_level,
        )

        # Upload to S3
        self._output_key = f"{self._output_prefix}/{output_zip_name}"
        await self._s3_repo.upload_file(
            str(output_zip_path),
            self._bucket,
            self._output_key,
        )

        Log.log().info(
            f"Uploaded flexibilized deck to s3://{self._bucket}/{self._output_key}"
        )

        # Cleanup output zip
        output_zip_path.unlink()


def factory(kind: str, *args, **kwargs) -> AbstractUnitOfWork:
    mappings: dict[str, type[AbstractUnitOfWork]] = {
        "FS": FSUnitOfWork,
        "S3": S3UnitOfWork,
    }
    return mappings[kind](*args, **kwargs)
