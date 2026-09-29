from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from patients.adapters.outbound.database.models import PatientModel
from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
)
from patients.application.ports.patient_repository import PatientRepositoryPort
from patients.domain.entities.patient import Patient


class PostgresPatientRepository(PatientRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, patient: Patient) -> Patient:
        model = self._to_model(patient)

        try:
            self._session.add(model)
            self._session.commit()
            self._session.refresh(model)
        except IntegrityError as exc:
            self._session.rollback()
            raise PatientConflictApplicationError(
                "Patient with provided unique attributes already exists"
            ) from exc

        return self._to_entity(model)

    def get_by_id(self, patient_id: str) -> Patient | None:
        statement = select(PatientModel).where(
            PatientModel.id == patient_id,
        )

        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_entity(model)

    def get_by_document(
        self,
        numero_documento: str,
    ) -> Patient | None:
        statement = select(PatientModel).where(
            PatientModel.numero_documento == numero_documento,
        )

        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_entity(model)

    def get_by_user_id(
        self,
        user_id: str,
    ) -> Patient | None:
        statement = select(PatientModel).where(
            PatientModel.user_id == user_id,
        )

        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_entity(model)

    def get_all(self) -> list[Patient]:
        statement = select(PatientModel).order_by(
            PatientModel.full_name,
        )

        models = self._session.scalars(statement).all()

        return [self._to_entity(model) for model in models]

    def update(self, patient: Patient) -> Patient:
        model = self._session.get(
            PatientModel,
            patient.id,
        )

        if model is None:
            raise ValueError(f"Patient not found: {patient.id}")

        model.user_id = patient.user_id
        model.tipo_documento = patient.tipo_documento
        model.numero_documento = patient.numero_documento
        model.full_name = patient.full_name
        model.fecha_nacimiento = patient.fecha_nacimiento
        model.telefono = patient.telefono
        model.email = patient.email
        model.direccion = patient.direccion
        model.is_active = patient.is_active
        model.updated_at = datetime.now(UTC)

        try:
            self._session.commit()
            self._session.refresh(model)
        except IntegrityError as exc:
            self._session.rollback()
            raise PatientConflictApplicationError(
                "Document or user is already associated with another patient"
            ) from exc

        return self._to_entity(model)

    def delete(self, patient_id: str) -> None:
        model = self._session.get(
            PatientModel,
            patient_id,
        )

        if model is not None:
            self._session.delete(model)
            self._session.commit()

    @staticmethod
    def _to_entity(model: PatientModel) -> Patient:
        return Patient(
            id=model.id,
            user_id=model.user_id,
            tipo_documento=model.tipo_documento,
            numero_documento=model.numero_documento,
            full_name=model.full_name,
            fecha_nacimiento=model.fecha_nacimiento,
            telefono=model.telefono,
            email=model.email,
            direccion=model.direccion,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_model(patient: Patient) -> PatientModel:
        now = datetime.now(UTC)

        return PatientModel(
            id=patient.id,
            user_id=patient.user_id,
            tipo_documento=patient.tipo_documento,
            numero_documento=patient.numero_documento,
            full_name=patient.full_name,
            fecha_nacimiento=patient.fecha_nacimiento,
            telefono=patient.telefono,
            email=patient.email,
            direccion=patient.direccion,
            is_active=patient.is_active,
            created_at=now,
            updated_at=now,
        )
