from abc import ABC, abstractmethod

from patients.domain.entities.patient import Patient


class PatientRepositoryPort(ABC):
    @abstractmethod
    def create(self, patient: Patient) -> Patient:
        pass

    @abstractmethod
    def get_by_id(self, patient_id: str) -> Patient | None:
        pass

    @abstractmethod
    def get_by_document(
        self,
        numero_documento: str,
    ) -> Patient | None:
        pass

    @abstractmethod
    def get_by_user_id(
        self,
        user_id: str,
    ) -> Patient | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Patient]:
        pass

    @abstractmethod
    def get_paginated(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Patient], int]:
        pass

    @abstractmethod
    def update(self, patient: Patient) -> Patient:
        pass

    @abstractmethod
    def delete(self, patient_id: str) -> None:
        pass
