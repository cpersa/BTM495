from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import select

from renova.models import StatusOfWork, Therapist


def test_get_patient_files(mock_session):
    therapist = Therapist(
        first_name="foo",
        last_name="bar",
        date_of_birth=date.today(),
        gender="neutral",
        pronouns="they/they",
        email_address="foo.bar@example.com",
        phone_number="(514) 999-9999",
        address="nowhere",
        license_number="nan",
        hiring_date=date.today(),
        years_of_experience=0,
        void_cheque=0,
        status_of_work=StatusOfWork.fulltime,
    )
