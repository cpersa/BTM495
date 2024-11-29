from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Optional

from sqlmodel import Field, Relationship

from renova.models.users import User

if TYPE_CHECKING:
    from renova.models import Appointment, EmergencyContact, PatientFile
    from renova.models.therapists import Therapist


class Client(User, table=True):
    emergency_contact_id: Annotated[
        int | None, Field(foreign_key="emergencycontact.id")
    ] = None
    emergency_contact: Optional["EmergencyContact"] = Relationship()
    appointments: list["Appointment"] = Relationship(back_populates="client")
    patient_file: Optional["PatientFile"] = Relationship(back_populates="client")

    def create_patient_file(
        self,
        primary_therapist: "Therapist",
        admission_date: datetime,
        insurance_number: str,
        blood_type: str,
        is_active: bool,
        discharge_date: datetime | None,
    ):
        pass
