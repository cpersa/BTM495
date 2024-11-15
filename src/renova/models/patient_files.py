from datetime import datetime
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel

from renova.models.users import Client, Therapist


class MedicalChart(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    patient_file_id: Annotated[int | None, Field(foreign_key="patientfile.id")] = None
    date: datetime
    note: str


class MedicalDocument(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    patient_file_id: Annotated[int | None, Field(foreign_key="patientfile.id")] = None
    date: datetime
    hospital_name: str


class Allergy(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    allergy_name: str
    severeness: str


class PatientFileAllergyLink(SQLModel, table=True):
    patient_file_id: Annotated[
        int, Field(foreign_key="patientfile.id", primary_key=True)
    ]
    allergy_id: Annotated[int, Field(foreign_key="allergy.id", primary_key=True)]


class EmergencyContact(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    contact_first_name: str
    contact_last_name: str
    contact_number: int
    contact_email: str


class Medication(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    medication_name: str
    dosage: str
    frequency: str


class PatientFileMedicationLink(SQLModel, table=True):
    patient_file_id: Annotated[
        int, Field(foreign_key="patientfile.id", primary_key=True)
    ]
    medication_id: Annotated[int, Field(foreign_key="medication.id", primary_key=True)]


class PatientFile(SQLModel, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    admission_date: datetime
    insurance_number: int
    blood_type: str
    active_status: bool
    discharge_date: datetime
    medical_charts: list[MedicalChart] = Relationship()
    medical_document: MedicalDocument = Relationship()
    allergies: list[Allergy] = Relationship(link_model=PatientFileAllergyLink)
    medications: list[Medication] = Relationship(link_model=PatientFileMedicationLink)
    client_id: Annotated[int | None, Field(foreign_key="client.id")] = None
    client: Client = Relationship()
    primary_therapist_id: Annotated[int | None, Field(foreign_key="therapist.id")] = None
    primary_therapist: Therapist = Relationship()
