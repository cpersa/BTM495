from typing import Annotated, Sequence

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import AfterValidator
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from renova.db import get_session
from renova.models.users import Therapist
router = APIRouter()


@router.post("/therapists")
def post_therapists(
    therapist: Annotated[Therapist, AfterValidator(Therapist.model_validate)], session: Session = Depends(get_session)
) -> Therapist:
    t = Therapist.model_validate(therapist)
    try:
        session.add(t)
        session.commit()
        session.refresh(t)
    except IntegrityError as e:
        raise HTTPException(403) from e

    return t


@router.get("/therapists")
def get_therapists(session: Session = Depends(get_session)) -> Sequence[Therapist]:
    return session.exec(select(Therapist)).all()
