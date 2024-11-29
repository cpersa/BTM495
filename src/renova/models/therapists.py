from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Relationship

from renova.models.users import User

if TYPE_CHECKING:
    from renova.models import PatientFile, ScheduleBlock


class StatusOfWork(str, Enum):
    fulltime = "FULLTIME"
    parttime = "PARTTIME"
    pending = "PENDING"


class Therapist(User, table=True):
    license_number: str
    hiring_date: date
    years_of_experience: int
    void_cheque: str
    status_of_work: StatusOfWork = StatusOfWork.pending
    schedule: list["ScheduleBlock"] = Relationship(back_populates="therapist")
    patient_files: list["PatientFile"] = Relationship(
        back_populates="primary_therapist"
    )

    @property
    def appointments(self):
        return [s.appointment for s in self.schedule if s.appointment is not None]

    def confirm(self, status: StatusOfWork):
        if status == StatusOfWork.pending:
            return
        self.status_of_work = status
