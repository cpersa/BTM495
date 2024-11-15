import os
from importlib import import_module

from sqlmodel import Session, SQLModel, create_engine

DB_URL = os.getenv("DB_URL", "sqlite:////var/lib/renova/renova.db")
ENGINE = create_engine(DB_URL, echo=os.getenv("DEBUG", False))


def get_session():
    with Session(ENGINE) as session:
        yield session


def init_db():
    import_module("renova.models")
    SQLModel.metadata.create_all(ENGINE)
