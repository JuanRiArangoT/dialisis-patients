from uuid import uuid4

from patients.application.dtos.create_patient import CreatePatientCommand
from patients.application.dtos.patient_output import PatientOutputDTO
from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
)
from patients.application.ports.patient_repository import PatientRepositoryPort
from patients.domain.entities.patient import Patient


class CreatePatientUseCase:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
    ) -> None:
        self._patient_repository = patient_repository

    def execute(
        self,
        command: CreatePatientCommand,
    ) -> PatientOutputDTO:
        existing_patient = self._patient_repository.get_by_document(
            command.numero_documento,
        )

        if existing_patient is not None:
            raise PatientConflictApplicationError(
                f"Patient already exists with document: {command.numero_documento}"
            )

        if command.user_id is not None:
            existing_patient = self._patient_repository.get_by_user_id(
                command.user_id,
            )

            if existing_patient is not None:
                raise PatientConflictApplicationError(
                    f"User already linked to a patient: {command.user_id}"
                )

        patient = Patient(
            id=str(uuid4()),
            user_id=command.user_id,
            tipo_documento=command.tipo_documento,
            numero_documento=command.numero_documento,
            full_name=command.full_name,
            fecha_nacimiento=command.fecha_nacimiento,
            telefono=command.telefono,
            email=command.email,
            direccion=command.direccion,
            is_active=True,
        )

        created_patient = self._patient_repository.create(patient)

        return PatientOutputDTO(
            patient_id=created_patient.id,
            user_id=created_patient.user_id,
            tipo_documento=created_patient.tipo_documento,
            numero_documento=created_patient.numero_documento,
            full_name=created_patient.full_name,
            fecha_nacimiento=created_patient.fecha_nacimiento,
            telefono=created_patient.telefono,
            email=created_patient.email,
            direccion=created_patient.direccion,
            is_active=created_patient.is_active,
        )
