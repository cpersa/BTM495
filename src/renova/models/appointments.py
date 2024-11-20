from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from renova.models.users import Therapist, Client


class AppointmentStatus(str, Enum):
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"


class Appointment(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    client_id: Annotated[int, Field(foreign_key="client.id")]
    client: "Client" = Relationship(back_populates="appointments")
    schedule_id: Annotated[int, Field(foreign_key="schedule.id")]
    schedule: "Schedule" = Relationship(back_populates="appointment")
    appointment_status: AppointmentStatus

    def cancel(self):
        self.appointment_status = AppointmentStatus.cancelled

    def reschedule(self, new_date: date):
        self.schedule


class Schedule(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    therapist_id: Annotated[int, Field(foreign_key="therapist.id")]
    therapist: "Therapist" = Relationship(back_populates="schedules")
    start_datetime: datetime
    end_datetime: datetime
    appointment: Appointment | None = Relationship(back_populates="schedule")
