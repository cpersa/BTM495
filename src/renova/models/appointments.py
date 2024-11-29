from datetime import datetime
from enum import Enum
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel
from renova.models.therapists import Therapist
from renova.models.clients import Client


class AppointmentStatus(str, Enum):
    pending = "PENDING"
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"


class Appointment(SQLModel, table=True):
    schedule_block_id: Annotated[
        int | None, Field(foreign_key="scheduleblock.id", primary_key=True)
    ] = None
    schedule_block: "ScheduleBlock" = Relationship(back_populates="appointment")
    client_id: Annotated[int | None, Field(foreign_key="client.id")] = None
    client: "Client" = Relationship(back_populates="appointments")
    appointment_status: AppointmentStatus = AppointmentStatus.pending

    def confirm(self):
        self.appointment_status = AppointmentStatus.confirmed

    def cancel(self):
        self.appointment_status = AppointmentStatus.cancelled

    def reschedule(self, schedule_block: "ScheduleBlock"):
        self.schedule_block = schedule_block


class ScheduleBlock(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    therapist_id: Annotated[int | None, Field(foreign_key="therapist.id")] = None
    therapist: "Therapist" = Relationship(back_populates="schedule")
    start_datetime: datetime
    end_datetime: datetime
    appointment: Appointment | None = Relationship(back_populates="schedule_block")

    def create_appointment(self, client: Client) -> Appointment:
        if self.appointment is not None:
            raise ValueError(f"schedule block {self.id} already has an appointment")
        self.appointment = Appointment(
            schedule_block=self,
            client=client,
            appointment_status=AppointmentStatus.pending,
        )

        return self.appointment
