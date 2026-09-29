from patients.application.dtos.patient_output import PatientOutputDTO
from patients.application.exceptions.patient_exceptions import (
    PatientNotFoundApplicationError,
)
from patients.application.ports.patient_repository import PatientRepositoryPort
from patients.domain.entities.patient import Patient


class DesactivatePatientUseCase:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
    ) -> None:
        self._patient_repository = patient_repository

    def execute(self, patient_id: str) -> PatientOutputDTO:
        patient = self._patient_repository.get_by_id(patient_id)

        if patient is None:
            raise PatientNotFoundApplicationError(f"Patient not found: {patient_id}")

        if not patient.is_active:
            return PatientOutputDTO(
                patient_id=patient.id,
                user_id=patient.user_id,
                tipo_documento=patient.tipo_documento,
                numero_documento=patient.numero_documento,
                full_name=patient.full_name,
                fecha_nacimiento=patient.fecha_nacimiento,
                telefono=patient.telefono,
                email=patient.email,
                direccion=patient.direccion,
                is_active=patient.is_active,
            )

        updated_patient = Patient(
            id=patient.id,
            user_id=patient.user_id,
            tipo_documento=patient.tipo_documento,
            numero_documento=patient.numero_documento,
            full_name=patient.full_name,
            fecha_nacimiento=patient.fecha_nacimiento,
            telefono=patient.telefono,
            email=patient.email,
            direccion=patient.direccion,
            is_active=False,
        )

        saved = self._patient_repository.update(updated_patient)

        return PatientOutputDTO(
            patient_id=saved.id,
            user_id=saved.user_id,
            tipo_documento=saved.tipo_documento,
            numero_documento=saved.numero_documento,
            full_name=saved.full_name,
            fecha_nacimiento=saved.fecha_nacimiento,
            telefono=saved.telefono,
            email=saved.email,
            direccion=saved.direccion,
            is_active=saved.is_active,
        )
