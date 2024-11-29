from datetime import date, datetime, timedelta
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Form, HTTPException, Query
from sqlmodel import col, or_, select

from renova.context import Context, get_context
from renova.models.appointments import Appointment, ScheduleBlock
from renova.models.clients import Client
from renova.models.therapists import Therapist

from .templates import templates

router = APIRouter()


class ClientContext(Context):
    def get_therapist(self, therapist_id: int) -> Therapist | None:
        return self.session.get(Therapist, therapist_id)

    def get_schedule(self, therapist: Therapist | None = None) -> list[ScheduleBlock]:
        if not therapist and self.client.patient_file:
            therapist = self.client.patient_file.primary_therapist
        if not therapist:
            return []
        return [b for b in therapist.schedule if b.appointment is None]

    def find_therapists(self, search: str) -> Sequence[Therapist]:
        if not search:
            therapists = self.session.exec(select(Therapist).limit(10)).all()
        else:
            therapists = self.session.exec(
                select(Therapist)
                .where(
                    or_(
                        col(Therapist.first_name).contains(search),
                        col(Therapist.last_name).contains(search),
                    ),
                )
                .limit(10)
            ).all()
        print(therapists)
        return therapists

    def get_schedule_block(self, schedule_block_id: int) -> ScheduleBlock | None:
        return self.session.get(ScheduleBlock, schedule_block_id)

    def book_appointment(self, schedule_block: ScheduleBlock) -> Appointment:
        if schedule_block.appointment is not None:
            raise ValueError(f"schedule block {schedule_block.id} is already book")
        appointment = Appointment(schedule_block=schedule_block, client=self.client)
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(self.client)
        self.session.refresh(appointment)
        self.session.refresh(schedule_block)
        return appointment

    def get_appointments(self) -> list[Appointment]:
        return self.client.appointments

    def cancel_appointment(self, appointment: Appointment) -> None:
        schedule_block = appointment.schedule_block
        appointment.cancel()
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(schedule_block)
        if schedule_block is not None:
            assert schedule_block.appointment is None

    def delete_appointment(self, schedule_block: ScheduleBlock) -> None:
        self.session.delete(schedule_block.appointment)
        self.session.commit()
        self.session.refresh(schedule_block)
        self.session.refresh(self.client)

    def get_start_of_week(self, day: date | None = None) -> date:
        today = day or date.today()
        return today - timedelta((today.weekday() + 1) % 7)

    def get_blocks(
        self, therapist: Therapist, day: date | None = None
    ) -> list[list[ScheduleBlock | None]]:
        start_of_week = datetime.combine(
            self.get_start_of_week(day), datetime.min.time()
        )
        blocks: list[list[ScheduleBlock | None]] = [
            [None for _ in range(24)] for _ in range(7)
        ]
        for block in self.session.exec(
            select(ScheduleBlock).where(
                ScheduleBlock.therapist_id == therapist.id,
                ScheduleBlock.start_datetime > start_of_week,
                ScheduleBlock.end_datetime < start_of_week + timedelta(weeks=1),
            )
        ).all():
            blocks[(block.start_datetime.weekday() + 1) % 7][
                block.start_datetime.hour
            ] = block
        return blocks


ClientCTX = Annotated[ClientContext, Depends(get_context(ClientContext, auth=Client))]


@router.get("/home")
def get_home_page(ctx: Annotated[Context, Depends(get_context(Context, auth=Client))]):
    print(ctx.client.appointments)
    return templates.TemplateResponse(
        ctx.request,
        "pages/home.html",
        context={
            "authenticated": ctx.authenticated,
            "appointments": ctx.client.appointments,
            "user": ctx.client,
        },
    )


@router.delete("/home/appointments/{schedule_block_id}")
def delete_appointment_from_home(
    ctx: ClientCTX,
    schedule_block_id: int,
):
    if (schedule_block := ctx.get_schedule_block(schedule_block_id)) is None:
        raise HTTPException(404, f"schedule block {schedule_block} not found")
    ctx.delete_appointment(schedule_block)
    return templates.TemplateResponse(
        ctx.request,
        "components/appointment_list.html",
        context={
            "authenticated": ctx.authenticated,
            "appointments": ctx.client.appointments,
            "user": ctx.client,
        },
    )


@router.get("/booking")
def get_booking_page(ctx: ClientCTX):
    return templates.TemplateResponse(
        ctx.request,
        "pages/booking.html",
        context={
            "authenticated": ctx.authenticated,
            "client": ctx.client,
            "therapists": ctx.find_therapists(""),
            "scheduling": True,
        },
    )


@router.get("/search_therapists")
def get_search_therapists(ctx: ClientCTX, search: str):
    return templates.TemplateResponse(
        ctx.request,
        "components/therapist_list.html",
        context={"therapists": ctx.find_therapists(search)},
    )


@router.get("/booking/{therapist_id}")
def get_booking_schedule_page(ctx: ClientCTX, therapist_id: int):
    if (therapist := ctx.get_therapist(therapist_id)) is None:
        raise HTTPException(404, f"therapist {therapist_id} not found")
    start_of_week = ctx.get_start_of_week()
    return templates.TemplateResponse(
        ctx.request,
        "pages/booking_schedule.html",
        context={
            "authenticated": ctx.authenticated,
            "client": ctx.client,
            "therapist": therapist,
            "date": start_of_week,
            "blocks": ctx.get_blocks(therapist, start_of_week),
            "ctx": ctx,
            "scheduling": True,
        },
    )


@router.put("/appointments/{schedule_block_id}")
def put_appointments(
    ctx: ClientCTX,
    schedule_block_id: int,
    weekday: Annotated[int, Form()],
    hour: Annotated[int, Form()],
):
    if (schedule_block := ctx.get_schedule_block(schedule_block_id)) is None:
        raise HTTPException(404, f"schedule block {schedule_block} not found")
    try:
        ctx.book_appointment(schedule_block)
    except ValueError as e:
        raise HTTPException(403) from e
    return templates.TemplateResponse(
        ctx.request,
        "components/appointment_block.html",
        context={
            "schedule_block": schedule_block,
            "weekday": weekday,
            "ctx": ctx,
            "hour": hour,
            "scheduling": True,
        },
    )


@router.delete("/appointments/{schedule_block_id}")
def delete_appointment(
    ctx: ClientCTX,
    schedule_block_id: int,
    weekday: Annotated[int, Query()],
    hour: Annotated[int, Query()],
):
    if (schedule_block := ctx.get_schedule_block(schedule_block_id)) is None:
        raise HTTPException(404, f"schedule block {schedule_block} not found")
    ctx.delete_appointment(schedule_block)
    return templates.TemplateResponse(
        ctx.request,
        "components/appointment_block.html",
        context={
            "schedule_block": schedule_block,
            "weekday": weekday,
            "ctx": ctx,
            "hour": hour,
            "scheduling": True,
        },
    )
