from abc import abstractmethod, ABC
from typing import List, Tuple, Dict, Type
import numpy as np  # type: ignore
from idecomp.decomp.dadger import Dadger
from idecomp.decomp.modelos.dadger import (
    UH,
    FC,
    TI,
    ACVAZMIN,
    ACVERTJU,
    ACNPOSNW,
    FP,
    HE,
    HV,
    LV,
    HQ,
    LQ,
    RE,
    LU,
)

from app.models.inviabilidade import Inviabilidade
from app.models.inviabilidade import InviabilidadeEV
from app.models.inviabilidade import InviabilidadeTI
from app.models.inviabilidade import InviabilidadeHV
from app.models.inviabilidade import InviabilidadeHQ
from app.models.inviabilidade import InviabilidadeRE
from app.models.inviabilidade import InviabilidadeHE
from app.models.inviabilidade import InviabilidadeDEFMIN
from app.models.inviabilidade import InviabilidadeFP
from app.models.inviabilidade import InviabilidadeDeficit
from app.models.flexibilizationresult import FlexibilizationResult
from app.utils.log import Log


class AbstractViolationRepository(ABC):
    tipos_inviabilidades = [
        InviabilidadeEV,
        InviabilidadeTI,
        InviabilidadeHV,
        InviabilidadeHQ,
        InviabilidadeRE,
        InviabilidadeHE,
        InviabilidadeDEFMIN,
        InviabilidadeFP,
        InviabilidadeDeficit,
    ]

    @abstractmethod
    def _flexibilizaEV(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeEV]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaTI(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeTI]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaHV(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeHV]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaHQ(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeHQ]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaRE(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeRE]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaHE(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeHE]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaDEFMIN(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeDEFMIN]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibilizaFP(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeFP]
    ) -> List[FlexibilizationResult]:
        pass

    @abstractmethod
    def _flexibiliza_deficit(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeDeficit]
    ) -> List[FlexibilizationResult]:
        pass

    def flexibilize(
        self, dadger: Dadger, inviabilidades: List[Inviabilidade]
    ) -> List[FlexibilizationResult]:
        # Agrupa as inviabilidades por tipo
        tipos = AbstractViolationRepository.tipos_inviabilidades
        invs_por_tipo: dict = {t: [] for t in tipos}
        for inv in inviabilidades:
            invs_por_tipo[type(inv)].append(inv)

        # Flexibiliza cada tipo
        flex_evs = self._flexibilizaEV(dadger, invs_por_tipo[InviabilidadeEV])
        flex_tis = self._flexibilizaTI(dadger, invs_por_tipo[InviabilidadeTI])
        flex_hvs = self._flexibilizaHV(dadger, invs_por_tipo[InviabilidadeHV])
        flex_hqs = self._flexibilizaHQ(dadger, invs_por_tipo[InviabilidadeHQ])
        flex_res = self._flexibilizaRE(dadger, invs_por_tipo[InviabilidadeRE])
        flex_hes = self._flexibilizaHE(dadger, invs_por_tipo[InviabilidadeHE])
        flex_defmins = self._flexibilizaDEFMIN(
            dadger, invs_por_tipo[InviabilidadeDEFMIN]
        )
        flex_fps = self._flexibilizaFP(dadger, invs_por_tipo[InviabilidadeFP])
        # PREMISSA
        # Só flexibiliza déficit se todas as inviabilidades forem déficit
        flex_defs = []
        if len(inviabilidades) == len(invs_por_tipo[InviabilidadeDeficit]):
            flex_defs = self._flexibiliza_deficit(
                dadger, invs_por_tipo[InviabilidadeDeficit]
            )
        return (
            flex_evs
            + flex_tis
            + flex_hvs
            + flex_hqs
            + flex_res
            + flex_hes
            + flex_defmins
            + flex_fps
            + flex_defs
        )


class AbsoluteViolationRepository(AbstractViolationRepository):
    deltas_inviabilidades: Dict[Type[Inviabilidade], float] = {
        InviabilidadeEV: 0,
        InviabilidadeTI: 0.2,
        InviabilidadeHV: 1,
        InviabilidadeHQ: 5,
        InviabilidadeRE: 1,
        InviabilidadeHE: 0.1,
        InviabilidadeDEFMIN: 0.2,
        InviabilidadeFP: 0,
        InviabilidadeDeficit: 2.0,
    }

    # Override
    def _flexibilizaEV(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeEV]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeEV) -> Tuple[int, int]:
            return (inv._codigo, inv._estagio)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeEV], inv_ini: InviabilidadeEV
        ) -> InviabilidadeEV:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        res: List[FlexibilizationResult] = []
        # Estrutura para conter os pares (código, estágio) já flexibilizados
        flexibilizados: List[Tuple[int, int]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            # Flexibiliza - Remove a consideração de evaporação na usina
            codigo = max_viol._codigo
            uh = dadger.uh(codigo_usina=codigo)
            assert isinstance(uh, UH)
            uh.evaporacao = False
            Log.log().info(
                f"Flexibilizando EV {codigo} "
                + f" ({max_viol._nome_usina}) - "
                + "Evaporação do registro UH desabilitada."
            )
            res.append(
                FlexibilizationResult(
                    flexType="EV",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=None,
                    flexLimit=None,
                    flexSubsystem=None,
                    flexAmount=None,
                )
            )
        return res

    # Override
    def _flexibilizaTI(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeTI]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeTI) -> Tuple[int, int]:
            return (inv._codigo, inv._estagio)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeTI], inv_ini: InviabilidadeTI
        ) -> InviabilidadeTI:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        res: List[FlexibilizationResult] = []
        # Estrutura para conter os pares (código, estágio) já flexibilizados
        flexibilizados: List[Tuple[int, int]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            # Flexibiliza
            Log.log().info(
                f"Flexibilizando TI {max_viol._codigo} -"
                + f" Estágio {max_viol._estagio}: "
            )
            idx = max_viol._estagio - 1
            reg = dadger.ti(codigo_usina=max_viol._codigo)
            assert isinstance(reg, TI)
            taxas = reg.taxa
            assert isinstance(taxas, list)
            valor_atual = taxas[idx]
            deltas = AbsoluteViolationRepository.deltas_inviabilidades
            valor_flex = max_viol._violacao + deltas[InviabilidadeTI]
            novo_valor = max([0, valor_atual - valor_flex])
            taxas[idx] = novo_valor
            reg.taxa = taxas
            Log.log().info(f"{valor_atual} -> {novo_valor}")
            res.append(
                FlexibilizationResult(
                    flexType="TI",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=None,
                    flexLimit=None,
                    flexSubsystem=None,
                    flexAmount=valor_flex,
                )
            )
        return res

    # Override
    def _flexibilizaHV(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeHV]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeHV) -> Tuple[int, int, str]:
            return (inv._codigo, inv._estagio, inv._limite)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeHV], inv_ini: InviabilidadeHV
        ) -> InviabilidadeHV:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        def __assegura_existencia_registros(inv: InviabilidadeHV):
            # "Cria" todas as LVs até o último estágio da restrição HV
            hv = dadger.hv(codigo_restricao=inv._codigo)
            assert isinstance(hv, HV)
            ei = hv.estagio_inicial
            ei = ei if ei else 1
            ef = hv.estagio_final
            ef = ef if ef else ei
            for e in range(ei, ef + 1):
                dadger.lv(codigo_restricao=max_viol._codigo, estagio=e)

        res: List[FlexibilizationResult] = []
        # Estrutura para conter as tuplas
        # (código, estágio, limite) já flexibilizados
        flexibilizados: List[Tuple[int, int, str]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            __assegura_existencia_registros(max_viol)
            # Flexibiliza
            reg = dadger.lv(
                codigo_restricao=max_viol._codigo, estagio=max_viol._estagio
            )
            assert isinstance(reg, LV)
            deltas = AbsoluteViolationRepository.deltas_inviabilidades
            Log.log().info(
                f"Flexibilizando HV {max_viol._codigo} - Estágio"
                + f" {max_viol._estagio}"
            )
            if max_viol._limite == "L. INF":
                # PREMISSA:
                # Uma HV que envolva mais de uma usina (tipo restrição
                # de igualdade de cotas), caso seja desejado flexibilizar
                # para um valor de L. INF negativo, espelha a restrição.
                valor_atual = reg.limite_inferior
                if valor_atual is None:
                    estagio_aux = max_viol._estagio
                    while (valor_atual is None) and (estagio_aux > 0):
                        estagio_aux -= 1
                        lv_aux = dadger.lv(
                            codigo_restricao=max_viol._codigo,
                            estagio=estagio_aux,
                        )
                        assert isinstance(lv_aux, LV)
                        valor_atual = lv_aux.limite_inferior

                assert isinstance(valor_atual, float)
                valor_flex = max_viol._violacao + deltas[InviabilidadeHV]
                # Confere quantos CV a HV possui:
                cvs_hv = dadger.cv(codigo_restricao=max_viol._codigo)
                if isinstance(cvs_hv, list):
                    novo_valor = valor_atual - valor_flex
                    if novo_valor < 0:
                        novo_valor = max([0, novo_valor])
                        # hv = dadger.hv(codigo_restricao=max_viol._codigo)
                        # for estagio in range(
                        #     hv.estagio_inicial, hv.estagio_final + 1
                        # ):
                        #     lv = dadger.lv(
                        #         codigo_restricao=max_viol._codigo, estagio=estagio
                        #     )
                        #     lv.limite_inferior, lv.limite_superior = (
                        #         lv.limite_superior,
                        #         lv.limite_inferior,
                        #     )
                        # for cv in cvs_hv:
                        #     cv.coeficiente *= -1
                else:
                    novo_valor = max([0, valor_atual - valor_flex])
                reg.limite_inferior = novo_valor
            elif max_viol._limite == "L. SUP":
                valor_atual = reg.limite_superior
                if valor_atual is None:
                    estagio_aux = max_viol._estagio
                    while (valor_atual is None) and (estagio_aux > 0):
                        estagio_aux -= 1
                        lv_aux = dadger.lv(
                            codigo_restricao=max_viol._codigo,
                            estagio=estagio_aux,
                        )
                        assert isinstance(lv_aux, LV)
                        valor_atual = lv_aux.limite_superior

                assert isinstance(valor_atual, float)
                valor_flex = max_viol._violacao + deltas[InviabilidadeHV]
                novo_valor = min([99999, valor_atual + valor_flex])
                reg.limite_superior = novo_valor
            Log.log().info(
                f" {max_viol._limite}: " + f"{valor_atual} -> {novo_valor}"
            )
            res.append(
                FlexibilizationResult(
                    flexType="HV",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=None,
                    flexLimit=identificacao[2],
                    flexSubsystem=None,
                    flexAmount=valor_flex,
                )
            )
        return res

    # Override
    def _flexibilizaHQ(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeHQ]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(
            inv: InviabilidadeHQ,
        ) -> Tuple[int, int, str, str]:
            return (inv._codigo, inv._estagio, inv._limite, inv._patamar)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeHQ], inv_ini: InviabilidadeHQ
        ) -> InviabilidadeHQ:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        def __assegura_existencia_registros(inv: InviabilidadeHQ):
            # "Cria" todas as LQs até o último estágio da restrição HQ
            hq = dadger.hq(codigo_restricao=inv._codigo)
            assert isinstance(hq, HQ)
            ei = hq.estagio_inicial
            ei = ei if ei else 1
            ef = hq.estagio_final
            ef = ef if ef else ei
            for e in range(ei, ef + 1):
                dadger.lq(codigo_restricao=max_viol._codigo, estagio=e)

        res: List[FlexibilizationResult] = []
        # Estrutura para conter as tuplas
        # (código, estágio, limite, patamar) já flexibilizados
        flexibilizados: List[Tuple[int, int, str, str]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            __assegura_existencia_registros(max_viol)
            # Flexibiliza
            reg = dadger.lq(
                codigo_restricao=max_viol._codigo, estagio=max_viol._estagio
            )
            assert isinstance(reg, LQ)
            deltas = AbsoluteViolationRepository.deltas_inviabilidades
            idx = max_viol._patamar - 1
            Log.log().info(
                f"Flexibilizando HQ {max_viol._codigo} - Estágio"
                + f" {max_viol._estagio} pat {max_viol._patamar}"
            )
            if max_viol._limite == "L. INF":
                limites = reg.limite_inferior
                assert isinstance(limites, list)
                valor_atual = limites[idx]
                if valor_atual is None:
                    estagio_aux = max_viol._estagio
                    while (valor_atual is None) and (estagio_aux > 0):
                        estagio_aux -= 1
                        lq_estagio = dadger.lq(
                            codigo_restricao=max_viol._codigo,
                            estagio=estagio_aux,
                        )
                        assert isinstance(lq_estagio, LQ)
                        limites_lq = lq_estagio.limite_inferior
                        assert isinstance(limites_lq, list)
                        valor_atual = limites_lq[idx]
                valor_flex = max_viol._violacao + deltas[InviabilidadeHQ]
                novo_valor = max([0, valor_atual - valor_flex])
                limites[idx] = novo_valor
                reg.limite_inferior = limites
            elif max_viol._limite == "L. SUP":
                limites = reg.limite_superior
                assert isinstance(limites, list)
                valor_atual = limites[idx]
                if valor_atual is None:
                    estagio_aux = max_viol._estagio
                    while (valor_atual is None) and (estagio_aux > 0):
                        estagio_aux -= 1
                        lq_estagio = dadger.lq(
                            codigo_restricao=max_viol._codigo,
                            estagio=estagio_aux,
                        )
                        assert isinstance(lq_estagio, LQ)
                        limites_lq = lq_estagio.limite_superior
                        assert isinstance(limites_lq, list)
                        valor_atual = limites_lq[idx]

                valor_flex = max_viol._violacao + deltas[InviabilidadeHQ]
                novo_valor = min([99999, valor_atual + valor_flex])
                limites[idx] = novo_valor
                reg.limite_superior = limites
            Log.log().info(
                f" {max_viol._limite}: " + f"{valor_atual} -> {novo_valor}"
            )
            res.append(
                FlexibilizationResult(
                    flexType="HQ",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=identificacao[3],
                    flexLimit=identificacao[2],
                    flexSubsystem=None,
                    flexAmount=valor_flex,
                )
            )
        return res

    # Override
    def _flexibilizaRE(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeRE]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(
            inv: InviabilidadeRE,
        ) -> Tuple[int, int, str, str]:
            return (inv._codigo, inv._estagio, inv._limite, inv._patamar)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeRE], inv_ini: InviabilidadeRE
        ) -> InviabilidadeRE:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        def __assegura_existencia_registros(inv: InviabilidadeRE):
            # "Cria" todas as LUs até o último estágio da restrição RE
            re = dadger.re(codigo_restricao=inv._codigo)
            assert isinstance(re, RE)
            ei = re.estagio_inicial
            ei = ei if ei else 1
            ef = re.estagio_final
            ef = ef if ef else ei
            for e in range(ei, ef + 1):
                dadger.lu(codigo_restricao=max_viol._codigo, estagio=e)

        res: List[FlexibilizationResult] = []
        # Estrutura para conter as tuplas
        # (código, estágio, limite, patamar) já flexibilizados
        flexibilizados: List[Tuple[int, int, str, str]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            __assegura_existencia_registros(max_viol)
            # Flexibiliza
            reg = dadger.lu(
                codigo_restricao=max_viol._codigo, estagio=max_viol._estagio
            )
            assert isinstance(reg, LU)
            deltas = AbsoluteViolationRepository.deltas_inviabilidades
            idx = max_viol._patamar - 1
            Log.log().info(
                f"Flexibilizando RE {max_viol._codigo} - Estágio"
                + f" {max_viol._estagio} pat {max_viol._patamar}"
            )
            if max_viol._limite == "L. INF":
                limites = reg.limite_inferior
                assert isinstance(limites, list)
                valor_atual = limites[idx]
                if valor_atual is None:
                    estagio_aux = max_viol._estagio
                    while (valor_atual is None) and (estagio_aux > 0):
                        estagio_aux -= 1
                        reg_aux = dadger.lu(
                            codigo_restricao=max_viol._codigo,
                            estagio=estagio_aux,
                        )
                        assert isinstance(reg_aux, LU)
                        limites_aux = reg_aux.limite_inferior
                        assert isinstance(limites_aux, list)
                        valor_atual = limites_aux[idx]

                valor_flex = max_viol._violacao + deltas[InviabilidadeRE]
                novo_valor = max([0, valor_atual - valor_flex])
                novos = reg.limite_inferior
                assert isinstance(novos, list)
                novos[idx] = novo_valor
                reg.limite_inferior = novos
            elif max_viol._limite == "L. SUP":
                limites = reg.limite_superior
                assert isinstance(limites, list)
                valor_atual = limites[idx]
                if valor_atual is None:
                    estagio_aux = max_viol._estagio
                    while (valor_atual is None) and (estagio_aux > 0):
                        estagio_aux -= 1
                        reg_aux = dadger.lu(
                            codigo_restricao=max_viol._codigo,
                            estagio=estagio_aux,
                        )
                        assert isinstance(reg_aux, LU)
                        limites_aux = reg_aux.limite_superior
                        assert isinstance(limites_aux, list)
                        valor_atual = limites_aux[idx]

                valor_flex = max_viol._violacao + deltas[InviabilidadeRE]
                novo_valor = min([99999, valor_atual + valor_flex])
                novos = reg.limite_superior
                assert isinstance(novos, list)
                novos[idx] = novo_valor
                reg.limite_superior = novos
            Log.log().info(
                f" {max_viol._limite}: " + f"{valor_atual} -> {novo_valor}"
            )
            res.append(
                FlexibilizationResult(
                    flexType="RE",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=identificacao[3],
                    flexLimit=identificacao[2],
                    flexSubsystem=None,
                    flexAmount=valor_flex,
                )
            )
        return res

    # Override
    def _flexibilizaFP(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeFP]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeFP) -> Tuple[int, int]:
            return (inv._codigo, inv._estagio)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeFP], inv_ini: InviabilidadeFP
        ) -> InviabilidadeFP:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        res: List[FlexibilizationResult] = []
        # Estrutura para conter os pares (código, estágio) já flexibilizados
        flexibilizados: List[Tuple[int, int]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            # Procura por um registro FP
            reg_fp = dadger.fp(codigo_usina=max_viol._codigo, estagio=1)
            if reg_fp is None:
                reg_ac = dadger.ac(max_viol._codigo, ACVERTJU)
                if reg_ac is None:
                    Log.log().warning(
                        "Flexibilizando FP - "
                        + "Não foi encontrado registro AC VERTJU"
                        + f" para a usina {max_viol._codigo} "
                        + f" ({max_viol._usina})"
                    )
                    ultimo_nposnw = dadger.ac(169, ACNPOSNW)
                    assert isinstance(ultimo_nposnw, ACNPOSNW)
                    reg_ac_novo = ACVERTJU()
                    reg_ac_novo.codigo_usina = max_viol._codigo
                    reg_ac_novo.considera_influencia = 0
                    dadger.data.add_after(ultimo_nposnw, reg_ac_novo)
                else:
                    Log.log().info(
                        "Flexibilizando FP - "
                        + "Registro AC VERTJU"
                        + f" para a usina {max_viol._codigo} "
                        + f" ({max_viol._usina}) = 0"
                    )
                    if isinstance(reg_ac, list):
                        for r in reg_ac:
                            assert isinstance(r, ACVERTJU)
                            r.considera_influencia = 0
                    elif isinstance(reg_ac, ACVERTJU):
                        reg_ac.considera_influencia = 0
                Log.log().warning(
                    "Flexibilizando FP - "
                    + "Não foi encontrado registro FP"
                    + f" para a usina {max_viol._codigo} "
                    + f" ({max_viol._usina})"
                )
                reg_fp_novo = FP()
                reg_fp_novo.codigo_usina = max_viol._codigo
                reg_fp_novo.estagio = 1
                reg_fp_novo.tipo_entrada_janela_turbinamento = 0
                reg_fp_novo.numero_pontos_turbinamento = 20
                reg_fp_novo.limite_inferior_janela_turbinamento = 0
                reg_fp_novo.limite_superior_janela_turbinamento = 100
                reg_fp_novo.tipo_entrada_janela_volume = 0
                reg_fp_novo.numero_pontos_volume = 20
                reg_fp_novo.limite_inferior_janela_volume = 100
                reg_fp_novo.limite_superior_janela_volume = 100
                reg_fc = dadger.fc(tipo="NEWCUT")
                assert isinstance(reg_fc, FC)
                dadger.data.add_after(reg_fc, reg_fp_novo)
                res.append(
                    FlexibilizationResult(
                        flexType="FP",
                        flexStage=identificacao[1],
                        flexCode=identificacao[0],
                        flexPatamar=None,
                        flexLimit=None,
                        flexSubsystem=None,
                        flexAmount=None,
                    )
                )
        return res

    # Override
    def _flexibilizaDEFMIN(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeDEFMIN]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeDEFMIN) -> Tuple[int, int, str]:
            return (inv._codigo, inv._estagio, inv._patamar)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeDEFMIN], inv_ini: InviabilidadeDEFMIN
        ) -> InviabilidadeDEFMIN:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        res: List[FlexibilizationResult] = []
        # Estrutura para conter os pares (código, estágio, patamar)
        # já flexibilizados
        flexibilizados: List[Tuple[int, int, str]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)

            reg_ac = dadger.ac(max_viol._codigo, ACVAZMIN)
            if reg_ac is None:
                Log.log().warning(
                    "Flexibilizando DEFMIN - "
                    + "Não foi encontrado registro AC VAZMIN"
                    + f" para a usina {max_viol._codigo} "
                    + f" ({max_viol._usina})"
                )
                reg_ac_novo = ACVAZMIN()
                reg_ac_novo.codigo_usina = max_viol._codigo
                reg_ac_novo.vazao = max_viol._vazmin_hidr
                ultimo_nposnw = dadger.ac(169, ACNPOSNW)
                assert isinstance(ultimo_nposnw, ACNPOSNW)
                dadger.data.add_after(ultimo_nposnw, reg_ac_novo)
                reg_ac = reg_ac_novo

            assert isinstance(reg_ac, ACVAZMIN)

            # Flexibiliza
            valor_flex = int(np.ceil(max_viol._violacao))
            vazao = reg_ac.vazao
            assert isinstance(vazao, int)
            novo_valor = np.max([0, -valor_flex])
            Log.log().info(
                f"Flexibilizando DEFMIN {max_viol._codigo} -"
                + f" Estágio {max_viol._estagio}:"
                + f" {reg_ac.vazao} -> {novo_valor}"
            )
            reg_ac.vazao = novo_valor
            res.append(
                FlexibilizationResult(
                    flexType="DEFMIN",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=identificacao[2],
                    flexLimit=None,
                    flexSubsystem=None,
                    flexAmount=valor_flex,
                )
            )
        return res

    # Override
    def _flexibilizaHE(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeHE]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeHE) -> Tuple[int, int, str]:
            return (inv._codigo, inv._estagio, inv._limite)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeHE], inv_ini: InviabilidadeHE
        ) -> InviabilidadeHE:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                if i._violacao > max_viol._violacao:
                    max_viol = i
            return max_viol

        res: List[FlexibilizationResult] = []
        # Estrutura para conter as tuplas
        # (código, estágio, limite) já flexibilizados
        flexibilizados: List[Tuple[int, int, str]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            # Flexibiliza
            reg = dadger.he(
                codigo_restricao=max_viol._codigo, estagio=max_viol._estagio
            )
            assert isinstance(reg, HE)
            Log.log().info(
                f"Flexibilizando HE {max_viol._codigo} - Estágio"
                + f" {max_viol._estagio}"
            )
            deltas = AbsoluteViolationRepository.deltas_inviabilidades
            if max_viol._limite != "L. INF":
                raise RuntimeError("Restrições RHE só aceitas para L. INF")
            if max_viol._unidade == "%":
                delta = deltas[InviabilidadeHE]
            if max_viol._unidade == "MWmes":
                delta = 100 * deltas[InviabilidadeHE]
            valor_atual = reg.limite
            if not valor_atual:
                valor_atual = 0.0
            valor_flex = max_viol._violacao + delta
            novo_valor = max([0, valor_atual - valor_flex])
            reg.limite = novo_valor
            Log.log().info(
                f" {max_viol._limite}: " + f"{valor_atual} -> {novo_valor}"
            )
            res.append(
                FlexibilizationResult(
                    flexType="HE",
                    flexStage=identificacao[1],
                    flexCode=identificacao[0],
                    flexPatamar=None,
                    flexLimit=identificacao[2],
                    flexSubsystem=None,
                    flexAmount=valor_flex,
                )
            )
        return res

    # Override
    def _flexibiliza_deficit(
        self, dadger: Dadger, inviabilidades: List[InviabilidadeDeficit]
    ) -> List[FlexibilizationResult]:
        def __identifica_inv(inv: InviabilidadeDeficit) -> Tuple[int, str]:
            return (inv._estagio, inv._subsistema)

        def __inv_maxima_violacao_identificada(
            invs: List[InviabilidadeDeficit], inv_ini: InviabilidadeDeficit
        ) -> InviabilidadeDeficit:
            max_viol = inv_ini
            ident_ini = __identifica_inv(inv_ini)
            invs_mesma_id = [
                i for i in invs if __identifica_inv(i) == ident_ini
            ]
            for i in invs_mesma_id:
                max_viol._violacao_percentual += i._violacao_percentual
            return max_viol

        # TODO - não precisar dessa constante de mapeamento SUB-REE
        rees_subsistema = {
            "SE": [1, 5, 6, 7, 10, 12],
            "S": [2, 11],
            "NE": [3],
            "N": [4, 8, 9],
        }

        res: List[FlexibilizationResult] = []
        # Estrutura para conter as tuplas
        # (estagio, subsis) já flexibilizados
        flexibilizados: List[Tuple[int, str]] = []
        for inv in inviabilidades:
            identificacao = __identifica_inv(inv)
            # Se já flexibilizou essa restrição nesse estágio, ignora
            if identificacao in flexibilizados:
                continue
            # Senão, procura dentre todas as outras pela maior violação
            flexibilizados.append(identificacao)
            max_viol = __inv_maxima_violacao_identificada(inviabilidades, inv)
            # Tenta flexibilizar todos os REEs daquele subsistema, que tiverem
            # restrições RHE
            for r in rees_subsistema[max_viol._subsistema]:
                # Lista as restrições RHE
                cms = dadger.cm()
                if cms is None:
                    return []
                assert isinstance(cms, list)
                cms_ree = [c for c in cms if c.codigo_ree == r]
                # Se tiver pelo menos um CM para o REE, flexibiliza os
                # RHE que existirem, para os respectivos estágios
                if len(cms_ree) > 0:
                    for cm in cms_ree:
                        reg = dadger.he(
                            codigo_restricao=cm.codigo_restricao,
                            estagio=max_viol._estagio,
                        )
                        if reg is None:
                            Log.log().warning(
                                "Não encontrada restrição HE com"
                                + f" código {cm.codigo_restricao} para "
                                + f"o estágio {max_viol._estagio}."
                            )
                            continue
                        assert isinstance(reg, HE)
                        valor_atual = reg.limite
                        if not valor_atual:
                            valor_atual = 0.0
                        deltas = (
                            AbsoluteViolationRepository.deltas_inviabilidades
                        )
                        delta = deltas[InviabilidadeDeficit]
                        valor_flex = max_viol._violacao_percentual + delta
                        novo_valor = max([0.0, valor_atual - valor_flex])
                        reg.limite = novo_valor
                        msg = (
                            f"Flexibilizando (DEFICIT) HE {reg.codigo_restricao} -"
                            + f"Estágio {max_viol._estagio} -"
                            + f"{reg.tipo_penalidade}: {valor_atual} ->"
                            + f" {novo_valor}"
                        )
                        Log.log().info(msg)
                        if novo_valor == 0:
                            Log.log().warning(
                                f"Valor da HE {reg.codigo_restricao} chegou a"
                                + " 0. e deveria ser"
                                + f" {valor_atual - valor_flex}"
                                + " pelo déficit"
                            )
                        res.append(
                            FlexibilizationResult(
                                flexType="DEFICIT",
                                flexStage=max_viol._estagio,
                                flexCode=reg.codigo_restricao,
                                flexPatamar=None,
                                flexLimit=None,
                                flexSubsystem=identificacao[1],
                                flexAmount=valor_flex,
                            )
                        )
        return res
