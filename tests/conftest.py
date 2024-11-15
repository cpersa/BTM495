import pytest
from sqlmodel import SQLModel, Session, create_engine
from renova.app import app
from renova.db import get_session

import tempfile


@pytest.fixture
def mock_session():
    with tempfile.NamedTemporaryFile(delete=True) as file:
        engine = create_engine(f"sqlite:///{file.name}")
        import renova.models  # noqa: F401
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            def get_session_override():
                return session
            try:
                app.dependency_overrides[get_session] = get_session_override
                yield session
            finally:
                del app.dependency_overrides[get_session]
