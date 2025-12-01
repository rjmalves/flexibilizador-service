"""Unit tests for Inviabilidade models.

This module tests the factory method and all Inviabilidade subclasses.
Tests for RE and HQ types are fully implemented using available fixtures.
Tests for other types (TI, EV, HV, HE, DEFMIN, FP, Deficit) are stubbed
with skip markers awaiting fixture files.
"""

import pandas as pd
import pytest

from app.models.inviabilidade import (
    Inviabilidade,
    InviabilidadeDeficit,
    InviabilidadeDEFMIN,
    InviabilidadeEV,
    InviabilidadeFP,
    InviabilidadeHE,
    InviabilidadeHQ,
    InviabilidadeHV,
    InviabilidadeRE,
    InviabilidadeTI,
)

# =============================================================================
# TestInviabilidadeFactory - Tests for factory method
# =============================================================================


class TestInviabilidadeFactory:
    """Tests for Inviabilidade.factory() static method."""

    def test_factory_creates_re_for_restricao_eletrica(self, hidr, relato):
        """Test factory creates InviabilidadeRE for RESTRICAO ELETRICA message."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RESTRICAO ELETRICA 45 PATAMAR 1 (L. INF)",
            "violacao": 10.0,
            "unidade": "MW",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeRE)

    def test_factory_creates_hq_for_rhq(self, hidr, relato):
        """Test factory creates InviabilidadeHQ for RHQ message."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RHQ 123: PATAMAR 2 (L. SUP)",
            "violacao": 5.0,
            "unidade": "m3/s",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeHQ)

    def test_factory_handles_missing_iteracao(self, hidr, relato):
        """Test factory handles rows without iteracao column."""
        linha = pd.Series({
            "estagio": 1,
            "cenario": 1,
            "restricao": "RESTRICAO ELETRICA 45 PATAMAR 1 (L. INF)",
            "violacao": 10.0,
            "unidade": "MW",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert inv._iteracao == -1

    def test_factory_raises_for_unknown_restriction(self, hidr, relato):
        """Test factory raises TypeError for unknown restriction type."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "UNKNOWN RESTRICTION TYPE",
            "violacao": 10.0,
            "unidade": "MW",
        })
        with pytest.raises(TypeError, match="não suportada"):
            Inviabilidade.factory(linha, hidr, relato)

    def test_factory_with_real_inviab_data(
        self, hidr, relato, inviabilidades_df
    ):
        """Test factory with real data from inviab_unic fixture."""
        for _, row in inviabilidades_df.iterrows():
            inv = Inviabilidade.factory(row, hidr, relato)
            assert isinstance(inv, Inviabilidade)
            assert inv._estagio == int(row["estagio"])
            assert inv._cenario == int(row["cenario"])

    def test_factory_preserves_violacao(self, hidr, relato):
        """Test factory preserves violacao value."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RESTRICAO ELETRICA 45 PATAMAR 1 (L. INF)",
            "violacao": 123.456,
            "unidade": "MW",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert inv._violacao == 123.456

    def test_factory_preserves_unidade(self, hidr, relato):
        """Test factory preserves unidade value."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RHQ 123: PATAMAR 2 (L. SUP)",
            "violacao": 5.0,
            "unidade": "m3/s",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert inv._unidade == "m3/s"


# =============================================================================
# TestInviabilidadeRE - Tests for electrical restriction
# =============================================================================


class TestInviabilidadeRE:
    """Tests for InviabilidadeRE class."""

    @pytest.fixture
    def re_linha_inf(self):
        """Sample RE infeasibility with L. INF limit."""
        return pd.Series({
            "iteracao": 1,
            "estagio": 2,
            "cenario": 3,
            "restricao": "RESTRICAO ELETRICA 45 PATAMAR 1 (L. INF)",
            "violacao": 150.5,
            "unidade": "MW",
        })

    @pytest.fixture
    def re_linha_sup(self):
        """Sample RE infeasibility with L. SUP limit."""
        return pd.Series({
            "iteracao": 2,
            "estagio": 1,
            "cenario": 5,
            "restricao": "RESTRICAO ELETRICA 123 PATAMAR 3 (L. SUP)",
            "violacao": 75.3,
            "unidade": "MW",
        })

    def test_re_parses_codigo(self, re_linha_inf, hidr, relato):
        """Test RE correctly extracts restriction code."""
        inv = Inviabilidade.factory(re_linha_inf, hidr, relato)
        assert inv._codigo == 45

    def test_re_parses_patamar(self, re_linha_inf, hidr, relato):
        """Test RE correctly extracts patamar."""
        inv = Inviabilidade.factory(re_linha_inf, hidr, relato)
        assert inv._patamar == 1

    def test_re_parses_limite_inferior(self, re_linha_inf, hidr, relato):
        """Test RE correctly identifies L. INF limit."""
        inv = Inviabilidade.factory(re_linha_inf, hidr, relato)
        assert inv._limite == "L. INF"

    def test_re_parses_limite_superior(self, re_linha_sup, hidr, relato):
        """Test RE correctly identifies L. SUP limit."""
        inv = Inviabilidade.factory(re_linha_sup, hidr, relato)
        assert inv._limite == "L. SUP"

    def test_re_preserves_base_attributes(self, re_linha_inf, hidr, relato):
        """Test RE preserves base class attributes."""
        inv = Inviabilidade.factory(re_linha_inf, hidr, relato)
        assert inv._iteracao == 1
        assert inv._estagio == 2
        assert inv._cenario == 3
        assert inv._violacao == 150.5
        assert inv._unidade == "MW"

    def test_re_str_representation(self, re_linha_inf, hidr, relato):
        """Test RE __str__ method includes key info."""
        inv = Inviabilidade.factory(re_linha_inf, hidr, relato)
        s = str(inv)
        assert "RE 45" in s
        assert "Pat 1" in s
        assert "L. INF" in s
        assert "Estágio 2" in s

    @pytest.mark.parametrize(
        "codigo,patamar,limite",
        [
            (1, 1, "L. INF"),
            (999, 3, "L. SUP"),
            (45, 2, "L. INF"),
        ],
    )
    def test_re_parses_various_formats(
        self, codigo, patamar, limite, hidr, relato
    ):
        """Test RE parses various restriction message formats."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": f"RESTRICAO ELETRICA {codigo} PATAMAR {patamar} ({limite})",
            "violacao": 10.0,
            "unidade": "MW",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert inv._codigo == codigo
        assert inv._patamar == patamar
        assert inv._limite == limite

    def test_re_from_real_fixture(self, hidr, relato, inviabilidades_df):
        """Test RE instances from real fixture data."""
        re_rows = inviabilidades_df[
            inviabilidades_df["restricao"].str.contains(
                "RESTRICAO ELETRICA", na=False
            )
        ]
        if re_rows.empty:
            pytest.skip("No RE infeasibilities in fixture")

        for _, row in re_rows.iterrows():
            inv = Inviabilidade.factory(row, hidr, relato)
            assert isinstance(inv, InviabilidadeRE)
            assert inv._codigo > 0
            assert inv._patamar >= 1
            assert inv._limite in ["L. INF", "L. SUP"]


# =============================================================================
# TestInviabilidadeHQ - Tests for hydraulic flow restriction
# =============================================================================


class TestInviabilidadeHQ:
    """Tests for InviabilidadeHQ class."""

    @pytest.fixture
    def hq_linha_inf(self):
        """Sample HQ infeasibility with L. INF limit."""
        return pd.Series({
            "iteracao": 1,
            "estagio": 3,
            "cenario": 2,
            "restricao": "RHQ 456: PATAMAR 1 (L. INF)",
            "violacao": 25.0,
            "unidade": "m3/s",
        })

    @pytest.fixture
    def hq_linha_sup(self):
        """Sample HQ infeasibility with L. SUP limit."""
        return pd.Series({
            "iteracao": 3,
            "estagio": 2,
            "cenario": 1,
            "restricao": "RHQ 789: PATAMAR 2 (L. SUP)",
            "violacao": 50.0,
            "unidade": "m3/s",
        })

    @pytest.fixture
    def hq_vazao_defluente(self):
        """Sample HQ with VAZAO DEFLUENTE format (from real fixture)."""
        return pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RHQ 258: VAZAO DEFLUENTE (L. INF), PATAMAR 3",
            "violacao": 10.0,
            "unidade": "m3/s",
        })

    def test_hq_parses_codigo(self, hq_linha_inf, hidr, relato):
        """Test HQ correctly extracts restriction code."""
        inv = Inviabilidade.factory(hq_linha_inf, hidr, relato)
        assert inv._codigo == 456

    def test_hq_parses_patamar(self, hq_linha_inf, hidr, relato):
        """Test HQ correctly extracts patamar."""
        inv = Inviabilidade.factory(hq_linha_inf, hidr, relato)
        assert inv._patamar == 1

    def test_hq_parses_limite_inferior(self, hq_linha_inf, hidr, relato):
        """Test HQ correctly identifies L. INF limit."""
        inv = Inviabilidade.factory(hq_linha_inf, hidr, relato)
        assert inv._limite == "L. INF"

    def test_hq_parses_limite_superior(self, hq_linha_sup, hidr, relato):
        """Test HQ correctly identifies L. SUP limit."""
        inv = Inviabilidade.factory(hq_linha_sup, hidr, relato)
        assert inv._limite == "L. SUP"

    def test_hq_preserves_base_attributes(self, hq_linha_inf, hidr, relato):
        """Test HQ preserves base class attributes."""
        inv = Inviabilidade.factory(hq_linha_inf, hidr, relato)
        assert inv._iteracao == 1
        assert inv._estagio == 3
        assert inv._cenario == 2
        assert inv._violacao == 25.0
        assert inv._unidade == "m3/s"

    def test_hq_str_representation(self, hq_linha_inf, hidr, relato):
        """Test HQ __str__ method includes key info."""
        inv = Inviabilidade.factory(hq_linha_inf, hidr, relato)
        s = str(inv)
        assert "HQ 456" in s
        assert "Pat 1" in s
        assert "L. INF" in s
        assert "Estágio 3" in s

    @pytest.mark.parametrize(
        "codigo,patamar,limite",
        [
            (1, 1, "L. INF"),
            (999, 3, "L. SUP"),
            (456, 2, "L. INF"),
        ],
    )
    def test_hq_parses_various_formats(
        self, codigo, patamar, limite, hidr, relato
    ):
        """Test HQ parses various restriction message formats."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": f"RHQ {codigo}: PATAMAR {patamar} ({limite})",
            "violacao": 10.0,
            "unidade": "m3/s",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert inv._codigo == codigo
        assert inv._patamar == patamar
        assert inv._limite == limite

    def test_hq_from_real_fixture(self, hidr, relato, inviabilidades_df):
        """Test HQ instances from real fixture data."""
        hq_rows = inviabilidades_df[
            inviabilidades_df["restricao"].str.contains("RHQ", na=False)
        ]
        if hq_rows.empty:
            pytest.skip("No HQ infeasibilities in fixture")

        for _, row in hq_rows.iterrows():
            inv = Inviabilidade.factory(row, hidr, relato)
            assert isinstance(inv, InviabilidadeHQ)
            assert inv._codigo > 0
            assert inv._patamar >= 1
            assert inv._limite in ["L. INF", "L. SUP"]


# =============================================================================
# STUB TESTS - Awaiting fixture files
# =============================================================================


class TestInviabilidadeTI:
    """Tests for InviabilidadeTI class (irrigation)."""

    @pytest.mark.skip(reason="Awaiting fixture file with TI infeasibilities")
    def test_ti_parses_codigo(self, hidr, relato):
        """Test TI correctly extracts plant code from hidr."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "IRRIGACAO, USINA NOME_USINA",
            "violacao": 10.0,
            "unidade": "m3/s",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeTI)

    @pytest.mark.skip(reason="Awaiting fixture file with TI infeasibilities")
    def test_ti_parses_nome_usina(self, hidr, relato):
        """Test TI correctly extracts plant name."""
        pass


class TestInviabilidadeEV:
    """Tests for InviabilidadeEV class (evaporation)."""

    @pytest.mark.skip(reason="Awaiting fixture file with EV infeasibilities")
    def test_ev_parses_codigo(self, hidr, relato):
        """Test EV correctly extracts plant code from hidr."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "EVAPORACAO, USINA NOME_USINA",
            "violacao": 10.0,
            "unidade": "hm3",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeEV)

    @pytest.mark.skip(reason="Awaiting fixture file with EV infeasibilities")
    def test_ev_parses_nome_usina(self, hidr, relato):
        """Test EV correctly extracts plant name."""
        pass


class TestInviabilidadeHV:
    """Tests for InviabilidadeHV class (volume restriction)."""

    @pytest.mark.skip(reason="Awaiting fixture file with HV infeasibilities")
    def test_hv_parses_codigo(self, hidr, relato):
        """Test HV correctly extracts restriction code."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RHV 123: (L. INF)",
            "violacao": 10.0,
            "unidade": "hm3",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeHV)
        assert inv._codigo == 123

    @pytest.mark.skip(reason="Awaiting fixture file with HV infeasibilities")
    def test_hv_parses_limite(self, hidr, relato):
        """Test HV correctly extracts limit type."""
        pass


class TestInviabilidadeHE:
    """Tests for InviabilidadeHE class (energy storage restriction)."""

    @pytest.mark.skip(reason="Awaiting fixture file with HE infeasibilities")
    def test_he_parses_codigo(self, hidr, relato):
        """Test HE correctly extracts restriction code."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "RESTRICAO RHE - NUMERO 456, PERIODO 2 (L. INF)",
            "violacao": 10.0,
            "unidade": "%",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeHE)

    @pytest.mark.skip(reason="Awaiting fixture file with HE infeasibilities")
    def test_he_parses_estagio(self, hidr, relato):
        """Test HE correctly extracts period/stage."""
        pass


class TestInviabilidadeDEFMIN:
    """Tests for InviabilidadeDEFMIN class (minimum flow deficit)."""

    @pytest.mark.skip(
        reason="Awaiting fixture file with DEFMIN infeasibilities"
    )
    def test_defmin_parses_codigo(self, hidr, relato):
        """Test DEFMIN correctly extracts plant code from hidr."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "DEF. MINIMA PATAMAR 1 USINA NOME_USINA",
            "violacao": 10.0,
            "unidade": "m3/s",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeDEFMIN)

    @pytest.mark.skip(
        reason="Awaiting fixture file with DEFMIN infeasibilities"
    )
    def test_defmin_parses_vazmin_hidr(self, hidr, relato):
        """Test DEFMIN extracts historical minimum flow from hidr."""
        pass


class TestInviabilidadeFP:
    """Tests for InviabilidadeFP class (production function)."""

    @pytest.mark.skip(reason="Awaiting fixture file with FP infeasibilities")
    def test_fp_parses_codigo(self, hidr, relato):
        """Test FP correctly extracts plant code from hidr."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "FUNCAO DE PRODUCAO USINA NOME_USINA, PATAMAR 1",
            "violacao": 10.0,
            "unidade": "MW",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeFP)

    @pytest.mark.skip(reason="Awaiting fixture file with FP infeasibilities")
    def test_fp_parses_patamar(self, hidr, relato):
        """Test FP correctly extracts patamar."""
        pass


class TestInviabilidadeDeficit:
    """Tests for InviabilidadeDeficit class (energy deficit)."""

    @pytest.mark.skip(
        reason="Awaiting fixture file with Deficit infeasibilities"
    )
    def test_deficit_parses_subsistema(self, hidr, relato):
        """Test Deficit correctly extracts subsystem."""
        linha = pd.Series({
            "iteracao": 1,
            "estagio": 1,
            "cenario": 1,
            "restricao": "DEFICIT SUBSISTEMA SE, PATAMAR 1",
            "violacao": 100.0,
            "unidade": "MWmed",
        })
        inv = Inviabilidade.factory(linha, hidr, relato)
        assert isinstance(inv, InviabilidadeDeficit)
        assert inv._subsistema == "SE"

    @pytest.mark.skip(
        reason="Awaiting fixture file with Deficit infeasibilities"
    )
    def test_deficit_calculates_violacao_percentual(self, hidr, relato):
        """Test Deficit calculates percentage violation from relato data."""
        pass
