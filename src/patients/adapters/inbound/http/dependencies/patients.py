from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from patients.adapters.inbound.http.dependencies.database import get_db
from patients.adapters.outbound.database.patient_repository import (
    PostgresPatientRepository,
)
from patients.application.ports.patient_repository import PatientRepositoryPort
from patients.application.use_cases.create_patient import CreatePatientUseCase
from patients.application.use_cases.delete_patient import DeletePatientUseCase
from patients.application.use_cases.get_patient import GetPatientUseCase
from patients.application.use_cases.list_patients import ListPatientsUseCase
from patients.application.use_cases.update_patient import UpdatePatientUseCase

DbSession = Annotated[Session, Depends(get_db)]


def get_patient_repository(
    db: DbSession,
) -> PatientRepositoryPort:
    return PostgresPatientRepository(db)


PatientRepository = Annotated[
    PatientRepositoryPort,
    Depends(get_patient_repository),
]


def get_create_patient_use_case(
    repository: PatientRepository,
) -> CreatePatientUseCase:
    return CreatePatientUseCase(repository)


def get_get_patient_use_case(
    repository: PatientRepository,
) -> GetPatientUseCase:
    return GetPatientUseCase(repository)


def get_list_patients_use_case(
    repository: PatientRepository,
) -> ListPatientsUseCase:
    return ListPatientsUseCase(repository)


def get_update_patient_use_case(
    repository: PatientRepository,
) -> UpdatePatientUseCase:
    return UpdatePatientUseCase(repository)


def get_delete_patient_use_case(
    repository: PatientRepository,
) -> DeletePatientUseCase:
    return DeletePatientUseCase(repository)
