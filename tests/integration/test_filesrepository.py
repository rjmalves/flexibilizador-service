"""Integration tests for RawFilesRepository."""

import pytest
from idecomp.decomp import Arquivos, Caso, Dadger, Hidr, InviabUnic, Relato

from app.adapters.filesrepository import RawFilesRepository


class TestRawFilesRepository:
    """Integration tests for RawFilesRepository with real fixture files."""

    @pytest.fixture
    def repo(self, extracted_deck_with_outputs):
        """Create repository with extracted deck directory."""
        return RawFilesRepository(str(extracted_deck_with_outputs))

    # =========================================================================
    # Caso and Arquivos Properties
    # =========================================================================

    def test_caso_reads_caso_dat(self, repo):
        """Test caso property reads caso.dat file."""
        caso = repo.caso
        assert isinstance(caso, Caso)
        assert caso.arquivos is not None

    def test_arquivos_reads_arquivos_file(self, repo):
        """Test arquivos property reads arquivos file (e.g., rv0)."""
        arq = repo.arquivos
        assert isinstance(arq, Arquivos)
        assert arq.dadger is not None

    # =========================================================================
    # get_dadger
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_dadger_returns_dadger(self, repo):
        """Test get_dadger returns parsed Dadger object."""
        dadger = await repo.get_dadger()
        assert isinstance(dadger, Dadger)

    @pytest.mark.asyncio
    async def test_get_dadger_caches_result(self, repo):
        """Test get_dadger caches result on subsequent calls."""
        dadger1 = await repo.get_dadger()
        dadger2 = await repo.get_dadger()
        assert dadger1 is dadger2

    @pytest.mark.asyncio
    async def test_get_dadger_has_registers(self, repo):
        """Test get_dadger returns Dadger with RE registers."""
        dadger = await repo.get_dadger()
        assert isinstance(dadger, Dadger)
        # Verify dadger has some RE registers
        re_regs = dadger.re()
        assert re_regs is not None

    # =========================================================================
    # set_dadger
    # =========================================================================

    @pytest.mark.asyncio
    async def test_set_dadger_writes_file(
        self, repo, extracted_deck_with_outputs
    ):
        """Test set_dadger writes modified Dadger back to file."""
        from app.internal.httpresponse import HTTPResponse

        dadger = await repo.get_dadger()
        assert isinstance(dadger, Dadger)

        result = repo.set_dadger(dadger)

        assert isinstance(result, HTTPResponse)
        assert result.code == 200

        # Verify file still exists
        dadger_path = extracted_deck_with_outputs / "dadger.rv0"
        assert dadger_path.exists()

    # =========================================================================
    # get_relato
    # =========================================================================

    def test_get_relato_returns_relato(self, repo):
        """Test get_relato returns parsed Relato object."""
        relato = repo.get_relato()
        assert isinstance(relato, Relato)

    def test_get_relato_caches_result(self, repo):
        """Test get_relato caches result on subsequent calls."""
        relato1 = repo.get_relato()
        relato2 = repo.get_relato()
        assert relato1 is relato2

    def test_get_relato_has_market_data(self, repo):
        """Test get_relato returns Relato with market data."""
        relato = repo.get_relato()
        assert isinstance(relato, Relato)
        # Relato should have some market data
        merc = relato.dados_mercado
        assert merc is not None

    # =========================================================================
    # get_inviabunic
    # =========================================================================

    def test_get_inviabunic_returns_inviabunic(self, repo):
        """Test get_inviabunic returns parsed InviabUnic object."""
        inviab = repo.get_inviabunic()
        assert isinstance(inviab, InviabUnic)

    def test_get_inviabunic_caches_result(self, repo):
        """Test get_inviabunic caches result on subsequent calls."""
        inviab1 = repo.get_inviabunic()
        inviab2 = repo.get_inviabunic()
        assert inviab1 is inviab2

    def test_get_inviabunic_has_infeasibilities(self, repo):
        """Test get_inviabunic returns InviabUnic with infeasibilities."""
        inviab = repo.get_inviabunic()
        assert isinstance(inviab, InviabUnic)
        df = inviab.inviabilidades_simulacao_final
        assert df is not None
        assert len(df) > 0

    # =========================================================================
    # get_hidr
    # =========================================================================

    def test_get_hidr_returns_hidr(self, repo):
        """Test get_hidr returns parsed Hidr object."""
        hidr = repo.get_hidr()
        assert isinstance(hidr, Hidr)
        assert hidr.cadastro is not None

    def test_get_hidr_caches_result(self, repo):
        """Test get_hidr caches result on subsequent calls."""
        hidr1 = repo.get_hidr()
        hidr2 = repo.get_hidr()
        assert hidr1 is hidr2

    def test_get_hidr_has_cadastro(self, repo):
        """Test get_hidr returns Hidr with plant cadastro."""
        hidr = repo.get_hidr()
        assert isinstance(hidr, Hidr)
        cadastro = hidr.cadastro
        assert cadastro is not None
        assert len(cadastro) > 0
