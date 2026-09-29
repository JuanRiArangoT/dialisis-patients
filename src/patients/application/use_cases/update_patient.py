from patients.application.dtos.patient_output import PatientOutputDTO
from patients.application.dtos.update_patient import UpdatePatientCommand
from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
    PatientNotFoundApplicationError,
)
from patients.application.ports.patient_repository import PatientRepositoryPort
from patients.domain.entities.patient import Patient


class UpdatePatientUseCase:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
    ) -> None:
        self._patient_repository = patient_repository

    def execute(
        self,
        patient_id: str,
        command: UpdatePatientCommand,
    ) -> PatientOutputDTO:
        existing_patient = self._patient_repository.get_by_id(
            patient_id,
        )

        if existing_patient is None:
            raise PatientNotFoundApplicationError(f"Patient not found: {patient_id}")

        patient_with_document = self._patient_repository.get_by_document(
            command.numero_documento,
        )

        if patient_with_document is not None and patient_with_document.id != patient_id:
            raise PatientConflictApplicationError(
                "Document is already associated with another patient"
            )

        if command.user_id is not None:
            patient_with_user = self._patient_repository.get_by_user_id(
                command.user_id,
            )

            if patient_with_user is not None and patient_with_user.id != patient_id:
                raise PatientConflictApplicationError(
                    "User is already associated with another patient"
                )

        patient = Patient(
            id=patient_id,
            user_id=command.user_id,
            tipo_documento=command.tipo_documento,
            numero_documento=command.numero_documento,
            full_name=command.full_name,
            fecha_nacimiento=command.fecha_nacimiento,
            telefono=command.telefono,
            email=command.email,
            direccion=command.direccion,
            is_active=command.is_active,
        )

        updated_patient = self._patient_repository.update(patient)

        return PatientOutputDTO(
            patient_id=updated_patient.id,
            user_id=updated_patient.user_id,
            tipo_documento=updated_patient.tipo_documento,
            numero_documento=updated_patient.numero_documento,
            full_name=updated_patient.full_name,
            fecha_nacimiento=updated_patient.fecha_nacimiento,
            telefono=updated_patient.telefono,
            email=updated_patient.email,
            direccion=updated_patient.direccion,
            is_active=updated_patient.is_active,
        )
