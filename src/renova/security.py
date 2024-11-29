from typing import Annotated

from fastapi import Cookie, Header, HTTPException, Request


async def check_csrf(
    request: Request,
    csrftoken: Annotated[str | None, Cookie()] = None,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> None:
    if request.method.lower() == "get":
        return
    if not csrftoken or not x_csrf_token or csrftoken != x_csrf_token:
        raise HTTPException(403, "CSRF check failed")
