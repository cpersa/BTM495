import enum
from datetime import datetime
from enum import Enum
from typing import Annotated

from sqlmodel import Field, SQLModel


class AppointmentStatus(str, Enum):
    confirmed = "CONFIRMED"
    canceled = "CANCELLED"


class Schedule(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    start_date: datetime
    end_date: datetime
    start_time: datetime
    end_time: datetime
    availability: bool


class Appointment(SQLModel, table=True):
    start_date: datetime
    end_date: datetime
    start_time: datetime
    end_time: datetime
    therapist_name: str
    client_name: str
    appointment_status: AppointmentStatus
