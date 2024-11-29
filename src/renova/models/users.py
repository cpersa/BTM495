from datetime import date
from typing import Annotated

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel):
    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    pronouns: str
    email_address: Annotated[EmailStr, Field(unique=True)]
    phone_number: str
    address: str
    hash: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Owner(User, table=True):
    pass
