from abc import ABC, abstractmethod
from typing import Dict, Type, Optional
import pathlib
from os.path import join

from idecomp.decomp.caso import Caso
from idecomp.decomp.arquivos import Arquivos
from idecomp.decomp.dadger import Dadger
from idecomp.decomp.inviabunic import InviabUnic
from idecomp.decomp.relato import Relato
from idecomp.decomp.hidr import Hidr

from app.internal.settings import Settings
from app.utils.encoding import converte_codificacao
from app.utils.log import Log
from app.internal.httpresponse import HTTPResponse


class AbstractFilesRepository(ABC):
    @property
    @abstractmethod
    def caso(self) -> Caso:
        raise NotImplementedError

    @property
    @abstractmethod
    def arquivos(self) -> Arquivos:
        raise NotImplementedError

    @abstractmethod
    async def get_dadger(self) -> Dadger:
        raise NotImplementedError

    @abstractmethod
    def set_dadger(self, d: Dadger) -> HTTPResponse:
        raise NotImplementedError

    @abstractmethod
    def get_inviabunic(self) -> Optional[InviabUnic]:
        raise NotImplementedError

    @abstractmethod
    def get_relato(self) -> Relato:
        raise NotImplementedError

    @abstractmethod
    def get_hidr(self) -> Hidr:
        raise NotImplementedError


class RawFilesRepository(AbstractFilesRepository):
    def __init__(self, tmppath: str):
        self.__tmppath = tmppath
        try:
            self.__caso = Caso.read(join(str(self.__tmppath), "caso.dat"))
        except FileNotFoundError as e:
            Log.log().error("Não foi encontrado o arquivo caso.dat")
            raise e
        self.__arquivos: Optional[Arquivos] = None
        self.__dadger: Optional[Dadger] = None
        self.__read_dadger = False
        self.__relato: Optional[Relato] = None
        self.__read_relato = False
        self.__inviabunic: Optional[InviabUnic] = None
        self.__read_inviabunic = False
        self.__hidr: Optional[Hidr] = None
        self.__read_hidr = False

    @property
    def caso(self) -> Caso:
        return self.__caso

    @property
    def arquivos(self) -> Arquivos:
        if self.__arquivos is None:
            try:
                self.__arquivos = Arquivos.read(
                    join(self.__tmppath, self.__caso.arquivos)
                )
            except FileNotFoundError as e:
                Log.log().error(
                    f"Não foi encontrado o arquivo {self.__caso.arquivos}"
                )
                raise e
        return self.__arquivos

    async def get_dadger(self) -> Dadger:
        if self.__read_dadger is False:
            self.__read_dadger = True
            try:
                caminho = pathlib.Path(self.__tmppath).joinpath(
                    self.arquivos.dadger
                )
                script = pathlib.Path(Settings.installdir).joinpath(
                    Settings.encoding_script
                )
                await converte_codificacao(caminho, script)
                Log.log().info(f"Lendo arquivo {self.arquivos.dadger}")
                self.__dadger = Dadger.read(caminho)
            except Exception as e:
                Log.log().error(
                    f"Erro na leitura do {self.arquivos.dadger}: {e}"
                )
                raise e
        return self.__dadger

    def set_dadger(self, d: Dadger) -> HTTPResponse:
        try:
            d.write(join(self.__tmppath, self.arquivos.dadger))
            return HTTPResponse(code=200, detail="")
        except Exception as e:
            return HTTPResponse(code=500, detail=str(e))

    def get_relato(self) -> Relato:
        if self.__read_relato is False:
            self.__read_relato = True
            try:
                Log.log().info(f"Lendo arquivo relato.{self.caso.arquivos}")
                self.__relato = Relato.read(
                    join(self.__tmppath, f"relato.{self.caso.arquivos}")
                )
            except Exception as e:
                Log.log().error(
                    f"Erro na leitura do relato.{self.caso.arquivos}: {e}"
                )
                raise e
        return self.__relato

    def get_inviabunic(self) -> Optional[InviabUnic]:
        if self.__read_inviabunic is False:
            self.__read_inviabunic = True
            try:
                Log.log().info(
                    f"Lendo arquivo inviab_unic.{self.caso.arquivos}"
                )
                self.__inviabunic = InviabUnic.read(
                    join(self.__tmppath, f"inviab_unic.{self.caso.arquivos}")
                )
            except FileNotFoundError as e:
                Log.log().info(
                    f"Não encontrado arquivo inviab_unic.{self.caso.arquivos}"
                )
                return None
            except Exception as e:
                Log.log().info(
                    f"Erro na leitura do inviab_unic.{self.caso.arquivos}: {e}"
                )
                return None
        return self.__inviabunic

    def get_hidr(self) -> Hidr:
        if self.__read_hidr is False:
            self.__read_hidr = True
            try:
                Log.log().info(f"Lendo arquivo {self.arquivos.hidr}")
                self.__hidr = Hidr.read(
                    join(self.__tmppath, self.arquivos.hidr)
                )
            except Exception as e:
                Log.log().error(
                    f"Erro na leitura do {self.arquivos.hidr}: {e}"
                )
                raise e
        return self.__hidr


def factory(kind: str, *args, **kwargs) -> AbstractFilesRepository:
    mapping: Dict[str, Type[AbstractFilesRepository]] = {
        "FS": RawFilesRepository
    }
    return mapping.get(kind)(*args, **kwargs)
