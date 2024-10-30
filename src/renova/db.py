import os

from sqlmodel import SQLModel, create_engine

import renova.models  # noqa: F401

DB_URL = os.getenv("DB_URL", "sqlite:////var/lib/renova/renova.db")
ENGINE = create_engine(DB_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(ENGINE)
