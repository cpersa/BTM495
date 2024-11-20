from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AfterValidator
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from renova.db import get_session
from renova.models import Appointment, Schedule, Therapist

router = APIRouter()


@router.post("/therapists")
def post_therapists(
    therapist: Annotated[Therapist, AfterValidator(Therapist.model_validate)],
    session: Session = Depends(get_session),
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


@router.get("/therapist/{therapist_id}")
def get_therapist(
    therapist_id: int, session: Annotated[Session, Depends(get_session)]
) -> Therapist:
    return session.exec(select(Therapist).where(Therapist.id == therapist_id)).one()


@router.post("/therapist/{therapist_id}/schedules")
def post_therapist_schedules(
    therapist_id: int,
    schedule: Annotated[Schedule, AfterValidator(Schedule.model_validate)],
    session: Annotated[Session, Depends(get_session)],
) -> Schedule:
    if schedule.therapist_id != therapist_id:
        # create a new object with the correct therapist_id
        schedule.id = None
        schedule.therapist_id = therapist_id
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


@router.get("/therapist/{therapist_id}/schedules")
def get_therapist_schedules(
    therapist_id: int, session: Annotated[Session, Depends(get_session)]
) -> Sequence[Schedule]:
    therapist = session.exec(
        select(Therapist).where(Therapist.id == therapist_id)
    ).one()
    return therapist.schedules


@router.post("/therapist/{therapist_id}/")


@router.get("/therapist/{therapist_id}/appointments")
def get_therapist_appointments(
    therapist_id: int, session: Annotated[Session, Depends(get_session)]
) -> Sequence[Appointment]:
    therapist = session.exec(
        select(Therapist).where(Therapist.id == therapist_id)
    ).one()
    return therapist.appointments
