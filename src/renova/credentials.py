import os
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, Response
from pydantic import BaseModel, ValidationError
from sqlmodel import Session

from renova.db import get_session
from renova.models.users import User

TOKEN_SECRET = os.getenv("RENOVA_MAIN_TOKEN_SECRET", "secret")


class Credential(BaseModel):
    id: int
    type: str


def authenticate(*, required: bool):
    async def wrapped(
        session: Annotated[Session, Depends(get_session)],
        credential: Annotated[str | None, Cookie()] = None,
    ) -> Credential | None:
        if credential is None:
            if required:
                raise HTTPException(401, "unauthorized")
            return None

        try:
            data = jwt.decode(credential, key=TOKEN_SECRET, algorithms=["HS256"])
        except jwt.InvalidSignatureError as e:
            if required:
                raise HTTPException(403, "forbidden") from e
            return None

        try:
            return Credential(**data)
        except ValidationError as e:
            if required:
                raise HTTPException(403, "forbidden") from e
            return None

    return wrapped


def login(user: User, response: Response) -> Response:
    token = jwt.encode(
        {"id": user.id, "type": type(user).__name__.lower()},
        key=TOKEN_SECRET,
        algorithm="HS256",
    )
    response.set_cookie("credential", token, path="/", samesite="strict", httponly=True)
    return response

def logout(response: Response) -> Response:
    response.delete_cookie("credential", path="/")
    return response
