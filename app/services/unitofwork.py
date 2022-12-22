from abc import ABC, abstractmethod
from os import chdir, curdir
from typing import Dict
from pathlib import Path

from app.adapters.filesrepository import (
    AbstractFilesRepository,
    RawFilesRepository,
)


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
        self._files = None

    def __create_repository(self):
        if self._files is None:
            self._files = RawFilesRepository(str(self._case_directory))

    def __enter__(self) -> "FSUnitOfWork":
        chdir(self._case_directory)
        self.__create_repository()
        return super().__enter__()

    def __exit__(self, *args):
        chdir(self._current_path)
        super().__exit__(*args)

    @property
    def files(self) -> RawFilesRepository:
        return self._files

    def rollback(self):
        pass


def factory(kind: str, *args, **kwargs) -> AbstractUnitOfWork:
    mappings: Dict[str, AbstractUnitOfWork] = {
        "FS": FSUnitOfWork,
    }
    return mappings[kind](*args, **kwargs)
