from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from renova.models import Appointment, EmergencyContact, Schedule


class User(SQLModel):
    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    pronouns: str
    email_address: str
    phone_number: str
    address: str


class StatusOfWork(str, Enum):
    fulltime = "FULLTIME"
    parttime = "PARTTIME"


class Therapist(User, table=True):
    license_number: str
    hiring_date: date
    years_of_experience: int
    void_cheque: int
    status_of_work: StatusOfWork
    schedules: list["Schedule"] = Relationship(back_populates="therapist")

    @property
    def appointments(self):
        return [s.appointment for s in self.schedules if s.appointment is not None]


class Owner(User, table=True):
    pass


class Client(User, table=True):
    emergency_contact_id: Annotated[
        int | None, Field(foreign_key="emergencycontact.id")
    ] = None
    emergency_contact: Optional["EmergencyContact"] = Relationship()
    appointments: list["Appointment"] = Relationship(back_populates="client")
