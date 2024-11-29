from typing import Annotated

from fastapi import Depends, Form, Query, Request
from fastapi.datastructures import URL
from pydantic import EmailStr, HttpUrl

from renova.context import get_context
from renova.credentials import login, logout
from renova.logins import LoginContext
from renova.main.client import router
from renova.main.templates import templates
from renova.models.clients import Client
from renova.models.therapists import Therapist
from renova.redirects import redirect


@router.post("/logout")
def post_logout(request: Request):
    return logout(redirect(request, 200, request.url_for("get_index")))


@router.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse(request, "pages/login.html")


@router.post("/login")
def post_login(
    login_ctx: Annotated[LoginContext, Depends(get_context(LoginContext, auth=False))],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
    redirect_url: Annotated[HttpUrl | None, Query()] = None,
):
    client = login_ctx.login(Client, email, password)
    return login(
        client,
        redirect(
            login_ctx.request, 200, redirect_url or router.url_path_for("get_home_page")
        ),
    )


@router.get("/dashboard/login")
def get_dashboard_login(
    request: Request, redirect: Annotated[HttpUrl | None, Query()] = None
):
    return templates.TemplateResponse(
        request,
        "pages/login.html",
        context={"redirect": redirect or request.url_for("get_dashboard")},
    )


@router.post("/dashboard/login")
def post_dashboard_login(
    ctx: Annotated[LoginContext, Depends(get_context(LoginContext, auth=False))],
    request: Request,
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
    redirect_url: Annotated[HttpUrl | None, Query()] = None,
):
    therapist = ctx.login(Therapist, email, password)
    return login(
        therapist,
        redirect(
            request,
            200,
            redirect_url or request.url_for("get_dashboard"),
        ),
    )
