from datetime import datetime
from enum import Enum
from typing import Annotated

from sqlmodel import Field, SQLModel


class User(SQLModel):
    id: Annotated[int, Field(primary_key=True)]
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    pronouns: str
    email_address: str
    phone_number: str
    address: str


class StatusOfWork(str, Enum):
    fulltime = "FULLTIME"
    parttime = "PARTTIME"


class Therapist(User, table=True):
    _license_number: str
    hiring_date: datetime
    years_of_experience: int
    _void_cheque: int
    status_of_work: StatusOfWork


class Owner(User, table=True):
    pass


class Client(User, table=True):
    emergency_contact_name: str
    emergency_contact_phone: int
