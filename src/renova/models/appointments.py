from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from renova.models.users import Therapist, Client


class AppointmentStatus(str, Enum):
    confirmed = "CONFIRMED"
    canceled = "CANCELLED"


class Appointment(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    client_id: Annotated[int | None, Field(foreign_key="client.id")] = None
    client: "Client" = Relationship(back_populates="appointments")
    schedule_id: Annotated[int | None, Field(foreign_key="schedule.id")] = None
    schedule: "Schedule" = Relationship(back_populates="appointment")
    appointment_status: AppointmentStatus


class Schedule(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    therapist_id: Annotated[int | None, Field(foreign_key="therapist.id")] = None
    therapist: "Therapist" = Relationship(back_populates="schedules")
    start_datetime: datetime
    end_datetime: datetime
    appointment: Appointment | None = Relationship(back_populates="schedule")
