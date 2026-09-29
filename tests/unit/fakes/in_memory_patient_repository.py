from patients.application.ports.patient_repository import PatientRepositoryPort
from patients.domain.entities.patient import Patient


class InMemoryPatientRepository(PatientRepositoryPort):
    def __init__(self) -> None:
        self.patients: dict[str, Patient] = {}

    def create(self, patient: Patient) -> Patient:
        self.patients[patient.id] = patient
        return patient

    def get_by_id(self, patient_id: str) -> Patient | None:
        return self.patients.get(patient_id)

    def get_by_document(self, numero_documento: str) -> Patient | None:
        for patient in self.patients.values():
            if patient.numero_documento == numero_documento:
                return patient
        return None

    def get_by_user_id(self, user_id: str) -> Patient | None:
        for patient in self.patients.values():
            if patient.user_id == user_id:
                return patient
        return None

    def get_all(self) -> list[Patient]:
        return sorted(self.patients.values(), key=lambda p: p.full_name)

    def get_paginated(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Patient], int]:
        filtered = list(self.patients.values())

        if is_active is not None:
            filtered = [p for p in filtered if p.is_active == is_active]

        if search:
            query = search.strip().lower()
            if query:
                filtered = [
                    p
                    for p in filtered
                    if query in p.full_name.lower()
                    or query in p.numero_documento.lower()
                ]

        filtered.sort(key=lambda p: p.full_name)
        total = len(filtered)
        offset = (page - 1) * page_size
        return filtered[offset : offset + page_size], total

    def update(self, patient: Patient) -> Patient:
        if patient.id not in self.patients:
            raise ValueError(f"Patient not found: {patient.id}")
        self.patients[patient.id] = patient
        return patient

    def delete(self, patient_id: str) -> None:
        patient = self.patients.get(patient_id)
        if patient is not None:
            self.patients[patient_id] = Patient(
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
