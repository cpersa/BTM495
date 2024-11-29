import os
from contextlib import contextmanager
from importlib import import_module
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

__all__ = ["make_session", "get_session", "init_db", "DBSession"]


DB_URL = os.getenv("DB_URL", "sqlite:////var/lib/renova/renova.db")
ENGINE = create_engine(DB_URL, echo=bool(os.getenv("DEBUG", False)))


@contextmanager
def make_session():
    with Session(ENGINE) as session:
        yield session


def get_session():
    with make_session() as session:
        yield session


def init_db():
    import_module("renova.models")
    SQLModel.metadata.create_all(ENGINE)


DBSession = Annotated[Session, Depends(get_session)]
