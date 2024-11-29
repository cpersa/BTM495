from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select

from renova.credentials import Credential, authenticate
from renova.db import DBSession
from renova.models.clients import Client
from renova.models.therapists import Therapist
from renova.models.users import Owner, User


class Context:
    def __init__(
        self, request: Request, session: Session, credential: Credential | None
    ):
        self.request = request
        self.session = session
        self.credential = credential

    @property
    def user(self) -> User:
        credential = self.credential
        if credential is None:
            raise HTTPException(401, "unauthorized")

        match self.credential:
            case "therapist":
                return self._get_user(Therapist, credential.id)
            case "client":
                return self._get_user(Client, credential.id)
            case "owner":
                return self._get_user(Owner, credential.id)
            case _:
                raise HTTPException(403, "forbidden")

    @property
    def owner(self) -> Owner:
        if self.credential is None:
            raise HTTPException(401, "unauthorized")
        if not self.credential.type == "owner":
            raise HTTPException(403, "forbidden")
        return self._get_user(Owner, self.credential.id)

    @property
    def therapist(self) -> Therapist:
        if self.credential is None:
            raise HTTPException(401, "unauthorized")
        if not self.credential.type == "therapist":
            raise HTTPException(403, "forbidden")
        return self._get_user(Therapist, self.credential.id)

    @property
    def client(self) -> Client:
        if self.credential is None:
            raise HTTPException(401, "unauthorized")
        if not self.credential.type == "client":
            raise HTTPException(403, "forbidden")
        return self._get_user(Client, self.credential.id)

    def _get_user[T: User](self, user_type: type[T], id: int) -> T:
        try:
            return self.session.exec(select(user_type).where(user_type.id == id)).one()
        except Exception as e:
            raise HTTPException(403, "forbidden") from e

    @property
    def authenticated(self) -> bool:
        return self.credential is not None


def get_context[C: Context](context_type: type[C], *, auth: type[User] | None | bool):
    def on_auth(
        request: Request,
        session: DBSession,
        credential: Annotated[
            Credential | None, Depends(authenticate(required=bool(auth)))
        ],
    ) -> C:
        ctx = context_type(request, session, credential)
        if (
            credential
            and isinstance(auth, type)
            and auth is not User
        ):
            ctx._get_user(auth, credential.id)
        return ctx

    return on_auth
