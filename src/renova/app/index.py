from contextlib import asynccontextmanager
from dataclasses import dataclass
from tkinter import W
from typing import Annotated, cast

import jwt
from fastapi import Depends, FastAPI, Request
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, PackageLoader
from sqlmodel import Session, select

from renova.app import therapists
from renova.db import get_session, init_db
from renova.models.users import Client, Therapist, User

templates = Jinja2Templates(env=Environment(loader=PackageLoader("renova.app")))

token_cookie = APIKeyCookie(name="session")


@dataclass
class Credential[T: User]:
    session: Session
    user: T

    @property
    def is_client(self) -> bool:
        return self.session.get(Client, self.user.id) is not None

    @property
    def is_therapist(self) -> bool:
        return self.session.get(Therapist, self.user.id) is not None


def authenticate_as[T: User](user_type: type[T]):
    async def authenticate(
        session: Annotated[Session, Depends(get_session)],
        token: Annotated[str, Depends(token_cookie)],
    ) -> Credential[T]:
        user = user_type.model_validate(jwt.decode(token))
        return Credential[T](session, user)

    return authenticate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(therapists.router)


@app.get("/")
def get_root(
    request: Request,
    credential: Annotated[Credential[User], Depends(authenticate_as(User))],
):
    return templates.TemplateResponse(request, "index.html")
