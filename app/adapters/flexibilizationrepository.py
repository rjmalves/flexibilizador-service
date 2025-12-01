from abc import ABC, abstractmethod

import pandas as pd  # type: ignore
from idecomp.decomp import Dadger, Hidr, InviabUnic, Relato

from app.adapters.violationrepository import AbsoluteViolationRepository
from app.internal.httpresponse import HTTPResponse
from app.models.flexibilizationresult import FlexibilizationResult
from app.models.flexibilizationrule import FlexibilizationRule
from app.models.inviabilidade import Inviabilidade
from app.services.unitofwork import AbstractUnitOfWork
from app.utils.log import Log


class AbstractFlexibilizationRepository(ABC):
    """ """

    @abstractmethod
    async def flex(
        self,
        rules: list[FlexibilizationRule],
        uow: AbstractUnitOfWork,
    ) -> list[FlexibilizationResult] | HTTPResponse:
        pass


class NEWAVEFlexibilizationRepository(AbstractFlexibilizationRepository):
    """ """

    async def flex(
        self,
        _rules: list[FlexibilizationRule],
        _uow: AbstractUnitOfWork,
    ) -> list[FlexibilizationResult] | HTTPResponse:
        return HTTPResponse(code=500, detail="NEWAVE not supported")


class DECOMPFlexibilizationRepository(AbstractFlexibilizationRepository):
    """ """

    async def flex(
        self,
        _rules: list[FlexibilizationRule],
        uow: AbstractUnitOfWork,
    ) -> list[FlexibilizationResult] | HTTPResponse:
        try:
            with uow:
                dadger = await uow.files.get_dadger()
                assert isinstance(dadger, Dadger)
                arq_inviab = uow.files.get_inviabunic()
                assert isinstance(arq_inviab, InviabUnic)
                inviab = arq_inviab.inviabilidades_simulacao_final
                assert isinstance(inviab, pd.DataFrame)
                relato = uow.files.get_relato()
                assert isinstance(relato, Relato)
                hidr = uow.files.get_hidr()
                assert isinstance(hidr, Hidr)
                # Cria as inviabilidades
                inviabilidades: list[Inviabilidade] = []
                for (
                    _,
                    linha,
                ) in inviab.iterrows():
                    inv = Inviabilidade.factory(linha, hidr, relato)
                    Log.log().info(inv)
                    inviabilidades.append(inv)
                Log.log().info(
                    f"Inviabilidades processadas com sucesso: {len(inviabilidades)}"
                )
                # Flexibiliza
                result = AbsoluteViolationRepository().flexibilize(
                    dadger, inviabilidades
                )
                Log.log().info("Inviabilidades flexibilizadas")
                uow.files.set_dadger(dadger)
                return result
        except Exception as e:
            return HTTPResponse(code=500, detail=str(e))


SUPPORTED_PROGRAMS: dict[str, type[AbstractFlexibilizationRepository]] = {
    "NEWAVE": NEWAVEFlexibilizationRepository,
    "DECOMP": DECOMPFlexibilizationRepository,
}
DEFAULT = DECOMPFlexibilizationRepository


def factory(
    kind: str | None, *args, **kwargs
) -> AbstractFlexibilizationRepository:
    if not kind:
        kind = ""
    return SUPPORTED_PROGRAMS.get(kind, DEFAULT)(*args, **kwargs)
