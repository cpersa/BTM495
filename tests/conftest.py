import tempfile
from contextlib import contextmanager
from importlib import import_module

import pytest
from sqlmodel import Session, SQLModel, create_engine

from renova.db import get_session
from renova.logins import LoginContext
from renova.main import app
from renova.main.signup import SignupContext


@contextmanager
def get_mock_session():
    with tempfile.NamedTemporaryFile(delete=True) as file:
        engine = create_engine(f"sqlite:///{file.name}")
        import_module("renova.models")

        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:

            def get_session_override():
                return session

            try:
                app.dependency_overrides[get_session] = get_session_override
                yield session
            finally:
                del app.dependency_overrides[get_session]


@pytest.fixture
def signup_ctx():
    with get_mock_session() as session:
        ctx = SignupContext(session, None)
        yield ctx


@pytest.fixture
def login_ctx():
    with get_mock_session() as session:
        ctx = LoginContext(session, None)
        yield ctx
