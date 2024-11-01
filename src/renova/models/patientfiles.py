from datetime import datetime
from enum import Enum
from typing import Annotated

from sqlmodel import Field, SQLModel


class PatientFile(SQLModel, table=True):
    patient_number: Annotated[int, Field(primary_key=True)]
    patient_first_name: str
    patient_last_name: str
    patient_date_birth: datetime
    admission_date: datetime
    patient_gender: str
    patient_address: str
    patient_phone: int
    patient_email: str
    insurance_number: int
    blood_type: str
    active_status: bool
    discharge_date: datetime
    primary_therapist: str


class MedicalChart(SQLModel, table=True):
    date: datetime
    note: str


class MedicalDocument(SQLModel, table=True):
    date: datetime
    hospital_name: str


class Allergy(SQLModel, table=True):
    allergy_name: str
    severeness: str


class EmergencyContact(SQLModel, table=True):
    contact_first_name: str
    contact_last_name: str
    contact_number: int
    contact_email: str


class Medication(SQLModel, table=True):
    medication_name: str
    dosage: str
    frequency: str
