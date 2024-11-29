from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from renova.context import get_context
from renova.credentials import login
from renova.logins import LoginContext
from renova.main.templates import templates
from renova.models.clients import Client
from renova.models.therapists import Therapist
from renova.redirects import redirect


class UserSignupForm(BaseModel):
    email_address: Annotated[EmailStr, Field()]
    password: Annotated[str, Field()]
    first_name: Annotated[str, Field()]
    last_name: Annotated[str, Field()]
    date_of_birth: Annotated[date, Field()]
    gender: Annotated[str, Field()]
    pronouns: Annotated[str, Field()]
    phone_number: Annotated[str, Field()]
    address: Annotated[str, Field()]


class TherapistSignupForm(UserSignupForm):
    license_number: Annotated[str, Form()]
    years_of_experience: Annotated[int, Form()]
    void_cheque: Annotated[str, Form()]


class SignupContext(LoginContext):
    def create_client(self, form: UserSignupForm) -> Client:
        data = form.model_dump()
        client = Client(
            email_address=data.pop("email_address"),
            hash=self.hash(data.pop("password")),
            **data,
        )
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def create_therapist(self, form: UserSignupForm) -> Therapist:
        data = form.model_dump()
        therapist = Therapist(
            email_address=data.pop("email_address"),
            hash=self.hash(data.pop("password")),
            hiring_date=date.today(),
            **data,
        )
        self.session.add(therapist)
        self.session.commit()
        self.session.refresh(therapist)
        return therapist


router = APIRouter()


@router.get("/signup")
def get_signup(request: Request, redirect: Annotated[HttpUrl | None, Query()] = None):
    return templates.TemplateResponse(
        request,
        "pages/signup.html",
        context={"redirect": redirect},
    )


@router.get("/signup/therapist")
def get_component_therapist_signup_form(
    request: Request, redirect_url: Annotated[HttpUrl | None, Query()] = None
):
    return templates.TemplateResponse(
        request,
        "pages/therapist_signup.html",
        context={"redirect": redirect_url},
    )


@router.post("/signup/therapist")
def post_therapist_signup(
    ctx: Annotated[SignupContext, Depends(get_context(SignupContext, auth=False))],
    *,
    redirect_url: Annotated[HttpUrl | None, Query()] = None,
    form: Annotated[TherapistSignupForm, Form()],
):
    therapist = ctx.create_therapist(form)
    return login(
        therapist,
        redirect(
            ctx.request,
            200,
            redirect_url or ctx.request.url_for("get_dashboard"),
        ),
    )


@router.get("/signup/client")
def get_component_client_signup_form(
    request: Request,
    redirect: Annotated[HttpUrl | None, Query()] = None,
):
    template = "pages/client_signup.html"
    redirect_str = str(redirect) if redirect else None
    return templates.TemplateResponse(
        request,
        template,
        context={"redirect": redirect_str},
    )


@router.post("/signup/client")
def post_signup(
    ctx: Annotated[SignupContext, Depends(get_context(SignupContext, auth=False))],
    request: Request,
    *,
    redirect_url: Annotated[HttpUrl | None, Query()] = None,
    form: Annotated[UserSignupForm, Form()],
):
    client = ctx.create_client(form)
    redirect_str = (
        str(redirect_url) if redirect_url else ctx.request.url_for("get_home_page")
    )
    return login(
        client,
        redirect(request, 200, redirect_str),
    )
