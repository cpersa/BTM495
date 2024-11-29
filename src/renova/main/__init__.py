import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from renova.context import Context, get_context
from renova.credentials import Credential, authenticate
from renova.db import init_db
from renova.redirects import redirect
from renova.security import check_csrf

from . import admin, client, login, signup, therapist
from .templates import templates

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan, dependencies=[Depends(check_csrf)])
app.include_router(therapist.router)
app.include_router(client.router)
app.include_router(admin.router)
app.include_router(signup.router)
app.include_router(login.router)
app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")


@app.get("/")
def get_index(
    request: Request,
    credential: Annotated[Credential | None, Depends(authenticate(required=False))],
):
    if credential is None:
        location = "get_signup"
    else:
        match credential.type:
            case "client":
                location = "get_home_page"
            case "therapist":
                location = "get_dashboard"
            case "owner":
                location = "get_admin_dashboard"
            case _:
                raise RuntimeError(f"unknown type {credential.type}")

    return redirect(request, 200, request.url_for(location))


@app.get("/error/{error_code}")
def get_error(ctx: Annotated[Context, Depends(get_context(Context, auth=False))], error_code: int):
    return templates.TemplateResponse(
        ctx.request, "pages/error.html", context={"error": error_code, "authenticated": ctx.authenticated}
    )
