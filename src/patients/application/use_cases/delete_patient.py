from patients.application.exceptions.patient_exceptions import (
    PatientNotFoundApplicationError,
)
from patients.application.ports.patient_repository import PatientRepositoryPort


class DeletePatientUseCase:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
    ) -> None:
        self._patient_repository = patient_repository

    def execute(self, patient_id: str) -> None:
        patient = self._patient_repository.get_by_id(patient_id)

        if patient is None:
            raise PatientNotFoundApplicationError(f"Patient not found: {patient_id}")

        self._patient_repository.delete(patient_id)
