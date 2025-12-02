"""End-to-end integration tests for flexibilization workflow."""

import os

import pytest

from app.adapters.flexibilizationrepository import (
    DECOMPFlexibilizationRepository,
    NEWAVEFlexibilizationRepository,
    factory,
)
from app.internal.httpresponse import HTTPResponse
from app.models.flexibilizationresult import FlexibilizationResult
from app.services.unitofwork import FSUnitOfWork


class TestDECOMPFlexibilizationRepository:
    """Integration tests for DECOMPFlexibilizationRepository."""

    @pytest.fixture
    def repo(self):
        """Create flexibilization repository."""
        return DECOMPFlexibilizationRepository()

    @pytest.fixture
    def uow(self, extracted_deck_with_outputs):
        """Create FSUnitOfWork with extracted deck."""
        return FSUnitOfWork(str(extracted_deck_with_outputs))

    @pytest.mark.asyncio
    async def test_flex_returns_results(self, repo, uow):
        """Test flex returns FlexibilizationResult list."""
        results = await repo.flex([], uow)

        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, FlexibilizationResult)

    @pytest.mark.asyncio
    async def test_flex_result_types(self, repo, uow):
        """Test flex results contain expected types (RE, HQ from fixture)."""
        results = await repo.flex([], uow)

        flex_types = {r.flexType for r in results}
        assert len(flex_types) > 0
        # Verify types are from known set
        known_types = {
            "RE",
            "HQ",
            "HV",
            "HE",
            "TI",
            "EV",
            "DEFMIN",
            "FP",
            "DEFICIT",
        }
        assert flex_types.issubset(known_types)

    @pytest.mark.asyncio
    async def test_flex_modifies_dadger(
        self, repo, uow, extracted_deck_with_outputs
    ):
        """Test flex writes modified dadger back to file."""
        dadger_path = extracted_deck_with_outputs / "dadger.rv0"
        original_mtime = os.path.getmtime(dadger_path)

        await repo.flex([], uow)

        new_mtime = os.path.getmtime(dadger_path)
        assert new_mtime >= original_mtime

    @pytest.mark.asyncio
    async def test_flex_returns_error_on_missing_dadger(self, temp_dir):
        """Test flex returns HTTPResponse when dadger missing."""
        caso_path = temp_dir / "caso.dat"
        caso_path.write_text("rv0")

        repo = DECOMPFlexibilizationRepository()
        uow = FSUnitOfWork(str(temp_dir))

        result = await repo.flex([], uow)

        assert isinstance(result, HTTPResponse)
        assert result.code == 500


class TestNEWAVEFlexibilizationRepository:
    """Tests for NEWAVEFlexibilizationRepository."""

    @pytest.mark.asyncio
    async def test_newave_returns_not_supported(self):
        """Test NEWAVE repository returns 500 not supported."""
        repo = NEWAVEFlexibilizationRepository()

        class MockUoW:
            pass

        result = await repo.flex([], MockUoW())

        assert isinstance(result, HTTPResponse)
        assert result.code == 500
        assert "not supported" in result.detail.lower()


class TestFlexibilizationRepositoryFactory:
    """Tests for flexibilization repository factory function."""

    def test_factory_decomp(self):
        """Test factory creates DECOMP repository."""
        repo = factory("DECOMP")
        assert isinstance(repo, DECOMPFlexibilizationRepository)

    def test_factory_newave(self):
        """Test factory creates NEWAVE repository."""
        repo = factory("NEWAVE")
        assert isinstance(repo, NEWAVEFlexibilizationRepository)

    def test_factory_default(self):
        """Test factory creates DECOMP as default."""
        repo = factory(None)
        assert isinstance(repo, DECOMPFlexibilizationRepository)

    def test_factory_unknown(self):
        """Test factory creates DECOMP for unknown kind."""
        repo = factory("UNKNOWN")
        assert isinstance(repo, DECOMPFlexibilizationRepository)


class TestFSUnitOfWork:
    """Tests for FSUnitOfWork context manager."""

    def test_fsuow_enters_and_exits(self, extracted_deck_with_outputs):
        """Test FSUnitOfWork can be used as context manager."""
        uow = FSUnitOfWork(str(extracted_deck_with_outputs))

        with uow as ctx:
            assert ctx is uow
            assert uow.files is not None

    def test_fsuow_provides_files_repository(self, extracted_deck_with_outputs):
        """Test FSUnitOfWork provides RawFilesRepository via files property."""
        from app.adapters.filesrepository import RawFilesRepository

        uow = FSUnitOfWork(str(extracted_deck_with_outputs))

        with uow:
            assert isinstance(uow.files, RawFilesRepository)

    @pytest.mark.asyncio
    async def test_fsuow_files_can_read_dadger(
        self, extracted_deck_with_outputs
    ):
        """Test files repository in UoW can read dadger."""
        from idecomp.decomp import Dadger

        uow = FSUnitOfWork(str(extracted_deck_with_outputs))

        with uow:
            dadger = await uow.files.get_dadger()
            assert isinstance(dadger, Dadger)
