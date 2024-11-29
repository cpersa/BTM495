from datetime import date, datetime

from sqlmodel import select

from renova.models.clients import Client
from renova.models.patient_files import PatientFile
from renova.models.therapists import StatusOfWork, Therapist


def test_get_patient_files(login_ctx):
    mock_session = login_ctx.session
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
        void_cheque="",
        status_of_work=StatusOfWork.fulltime,
        hash=login_ctx.hash("some password"),
    )
    client = Client(
        first_name="foo",
        last_name="bar",
        date_of_birth=date.today(),
        gender="neutral",
        pronouns="they/they",
        email_address="foo.bar@example.com",
        phone_number="(514) 999-9999",
        address="nowhere",
        hash=login_ctx.hash("some password"),
    )
    patient_files = [
        PatientFile(
            admission_date=datetime.today(),
            insurance_number="000000000",
            blood_type="o",
            is_active=True,
            discharge_date=datetime.today(),
            client=client,
            primary_therapist=therapist,
        )
    ]
    mock_session.add(therapist)
    mock_session.add(client)
    mock_session.add_all(patient_files)
    mock_session.commit()

    patient_files = mock_session.exec(
        select(PatientFile).where(PatientFile.primary_therapist_id == therapist.id)
    ).all()

    assert all(f.primary_therapist == therapist for f in patient_files)
