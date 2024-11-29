from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from renova.context import Context, get_context
from renova.models.appointments import Appointment, ScheduleBlock
from renova.models.clients import Client
from renova.models.patient_files import PatientFile
from renova.models.therapists import Therapist
from renova.redirects import redirect
from renova.security import check_csrf

from .templates import templates


class NotPrimaryTherapistError(RuntimeError):
    pass


class TherapistContext(Context):
    def get_schedule_block(self, schedule_block_id: int) -> ScheduleBlock:
        try:
            return self.session.exec(
                select(ScheduleBlock).where(ScheduleBlock.id == schedule_block_id)
            ).one()
        except NoResultFound as e:
            raise IndexError(f"schedule block {schedule_block_id} not found") from e

    def confirm_appointment(self, appointment: Appointment):
        appointment.confirm()
        self.session.add(appointment)
        self.session.commit()

    def get_client(self, client_id: int) -> Client:
        try:
            return self.session.exec(select(Client).where(Client.id == client_id)).one()
        except NoResultFound as e:
            raise IndexError(f"client {client_id} not found") from e

    def create_appointment(self, schedule_block_id: int, client_id: int) -> Appointment:
        schedule_block = self.get_schedule_block(schedule_block_id)
        client = self.get_client(client_id)
        appointment = schedule_block.create_appointment(client)
        appointment.confirm()
        self.session.add(schedule_block)
        self.session.add(appointment)
        self.session.commit()
        return appointment

    def create_schedule_block(self, start: datetime):
        end = start + timedelta(hours=1)
        schedule_block = ScheduleBlock(
            therapist=self.therapist, start_datetime=start, end_datetime=end
        )
        self.session.add(schedule_block)
        self.session.commit()
        self.session.refresh(schedule_block)
        return schedule_block

    def delete_schedule_block(self, schedule_block_id: int):
        schedule_block = self.session.get(ScheduleBlock, schedule_block_id)
        self.session.delete(schedule_block)
        self.session.commit()

    def update_schedule_block(
        self, schedule_block: ScheduleBlock, start: datetime, end: datetime
    ):
        schedule_block.start_datetime = start
        schedule_block.end_datetime = end
        self.session.add(schedule_block)
        self.session.commit()

    def update_patient_file(
        self,
        client_id,
        admission_date: datetime,
        insurance_number: str,
        blood_type: str,
        is_active: bool,
        discharge_date: datetime | None,
    ) -> PatientFile:
        client = self.get_client(client_id)
        if (
            client.patient_file is not None
            and client.patient_file.primary_therapist != self.user
        ):
            raise NotPrimaryTherapistError(
                f"therapist {self.user.id} is not the primary therapist of client {client_id}"
            )
        client.patient_file = PatientFile(
            primary_therapist=self.therapist,
            admission_date=admission_date,
            insurance_number=insurance_number,
            blood_type=blood_type,
            is_active=is_active,
            discharge_date=discharge_date,
        )
        self.session.add_all([client, client.patient_file])
        self.session.commit()
        return client.patient_file

    def get_start_of_week(self, day: date | None = None) -> date:
        today = day or date.today()
        return today - timedelta((today.weekday() + 1) % 7)

    def get_blocks(self, day: date | None = None) -> list[list[ScheduleBlock | None]]:
        start_of_week = datetime.combine(
            self.get_start_of_week(day), datetime.min.time()
        )
        blocks: list[list[ScheduleBlock | None]] = [
            [None for _ in range(24)] for _ in range(7)
        ]
        for block in self.session.exec(
            select(ScheduleBlock).where(
                ScheduleBlock.therapist_id == self.therapist.id,
                ScheduleBlock.start_datetime > start_of_week,
                ScheduleBlock.end_datetime < start_of_week + timedelta(weeks=1),
            )
        ).all():
            blocks[(block.start_datetime.weekday() + 1) % 7][
                block.start_datetime.hour
            ] = block
        return blocks


router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    ctx: Annotated[
        TherapistContext, Depends(get_context(TherapistContext, auth=False))
    ],
):
    if not ctx.authenticated:
        return redirect(
            ctx.request,
            401,
            ctx.request.url_for("get_dashboard_login").include_query_params(
                redirect=ctx.request.url
            ),
        )
    start_of_week = ctx.get_start_of_week()
    return templates.TemplateResponse(
        ctx.request,
        "pages/dashboard.html",
        context={
            "authenticated": ctx.authenticated,
            "therapist": ctx.therapist,
            "date": start_of_week,
            "blocks": ctx.get_blocks(),
        },
    )


@router.post("/schedule")
def post_schedules(
    ctx: Annotated[
        TherapistContext, Depends(get_context(TherapistContext, auth=Therapist))
    ],
    weekday: Annotated[int, Form()],
    hour: Annotated[int, Form()],
):
    start = datetime.combine(ctx.get_start_of_week(), datetime.min.time()) + timedelta(
        days=weekday, hours=hour
    )
    schedule_block = ctx.create_schedule_block(start)
    return templates.TemplateResponse(
        ctx.request,
        "components/schedule_block.html",
        context={
            "therapist": ctx.therapist,
            "schedule_block": schedule_block,
            "weekday": weekday,
            "hour": hour,
        },
    )


@router.put("/schedule/{schedule_block_id}/confirm")
def put_schedule_block_confirm(
    ctx: Annotated[
        TherapistContext, Depends(get_context(TherapistContext, auth=Therapist))
    ],
    schedule_block_id: int,
    weekday: Annotated[int, Form()],
    hour: Annotated[int, Form()],
):
    if (schedule_block := ctx.get_schedule_block(schedule_block_id)) is None or schedule_block.appointment is None:
        raise HTTPException(404, f"appointment for schedule block {schedule_block_id} not found")
    ctx.confirm_appointment(schedule_block.appointment)
    return templates.TemplateResponse(
        ctx.request,
        "components/schedule_block.html",
        context={
            "therapist": ctx.therapist,
            "weekday": weekday,
            "hour": hour,
            "schedule_block": schedule_block,
        },
    )


@router.delete("/schedule/{schedule_block_id}")
def delete_schedules(
    ctx: Annotated[
        TherapistContext, Depends(get_context(TherapistContext, auth=Therapist))
    ],
    schedule_block_id: int,
    weekday: Annotated[int, Query()],
    hour: Annotated[int, Query()],
):
    ctx.delete_schedule_block(schedule_block_id)
    return templates.TemplateResponse(
        ctx.request,
        "components/schedule_block.html",
        context={
            "therapist": ctx.therapist,
            "weekday": weekday,
            "hour": hour,
            "schedule_block": None,
        },
    )


@router.put("/clients/{client_id}/patient_file", dependencies=[Depends(check_csrf)])
def put_patient_file(
    ctx: Annotated[TherapistContext, Depends(get_context(TherapistContext, auth=True))],
    request: Request,
    client_id: int,
    admission_date: Annotated[datetime, Form()],
    insurance_number: Annotated[str, Form()],
    blood_type: Annotated[str, Form()],
    is_active: Annotated[bool, Form()],
    discharge_date: Annotated[datetime, Form()],
):
    patient_file = ctx.update_patient_file(
        client_id=client_id,
        admission_date=admission_date,
        insurance_number=insurance_number,
        blood_type=blood_type,
        is_active=is_active,
        discharge_date=discharge_date,
    )
    return templates.TemplateResponse(
        request, "components/patient_file.html", context={"patient_file": patient_file}
    )
