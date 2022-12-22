from abc import ABC, abstractmethod
from typing import Dict, List, Union

from app.internal.httpresponse import HTTPResponse
from app.models.flexibilizationrule import FlexibilizationRule
from app.models.flexibilizationresult import FlexibilizationResult
from app.models.inviabilidade import Inviabilidade
from app.adapters.violationrepository import AbsoluteViolationRepository
from app.services.unitofwork import AbstractUnitOfWork
from app.utils.log import Log


class AbstractFlexibilizationRepository(ABC):
    """ """

    @abstractmethod
    async def flex(
        self,
        rules: List[FlexibilizationRule],
        uow: AbstractUnitOfWork,
    ) -> Union[List[FlexibilizationResult], HTTPResponse]:
        pass


class NEWAVEFlexibilizationRepository(AbstractFlexibilizationRepository):
    """ """

    async def flex(
        self,
        rules: List[FlexibilizationRule],
        uow: AbstractUnitOfWork,
    ) -> Union[List[FlexibilizationResult], HTTPResponse]:
        return HTTPResponse(code=500, detail="NEWAVE not supported")


class DECOMPFlexibilizationRepository(AbstractFlexibilizationRepository):
    """ """

    async def flex(
        self,
        rules: List[FlexibilizationRule],
        uow: AbstractUnitOfWork,
    ) -> Union[List[FlexibilizationResult], HTTPResponse]:
        try:
            with uow:
                dadger = await uow.files.get_dadger()
                inviab = uow.files.get_inviabunic().inviabilidades_iteracoes
                relato = uow.files.get_relato()
                hidr = uow.files.get_hidr()
                # Cria as inviabilidades
                inviabilidades: List[Inviabilidade] = []
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


SUPPORTED_PROGRAMS: Dict[str, AbstractFlexibilizationRepository] = {
    "NEWAVE": NEWAVEFlexibilizationRepository,
    "DECOMP": DECOMPFlexibilizationRepository,
}
DEFAULT = DECOMPFlexibilizationRepository


def factory(kind: str, *args, **kwargs) -> AbstractFlexibilizationRepository:
    s = SUPPORTED_PROGRAMS.get(kind)
    if s is None:
        return DEFAULT(*args, **kwargs)
    return s(*args, **kwargs)
