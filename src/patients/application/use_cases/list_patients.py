import math

from patients.application.dtos.list_patients_query import ListPatientsQuery
from patients.application.dtos.patient_output import (
    PaginatedPatientsOutputDTO,
    PatientOutputDTO,
)
from patients.application.ports.patient_repository import PatientRepositoryPort


class ListPatientsUseCase:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
    ) -> None:
        self._patient_repository = patient_repository

    def execute(
        self,
        query: ListPatientsQuery | None = None,
    ) -> PaginatedPatientsOutputDTO:
        params = query or ListPatientsQuery()

        patients, total = self._patient_repository.get_paginated(
            page=params.page,
            page_size=params.page_size,
            search=params.search,
            is_active=params.is_active,
        )

        items = [
            PatientOutputDTO(
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
            for patient in patients
        ]

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        return PaginatedPatientsOutputDTO(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )
