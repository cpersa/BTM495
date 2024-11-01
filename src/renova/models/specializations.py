from typing import Annotated

from sqlmodel import Field, SQLModel


class Specialization(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    specializationType: str
    years_of_experience: int