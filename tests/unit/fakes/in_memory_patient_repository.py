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

    def update(self, patient: Patient) -> Patient:
        if patient.id not in self.patients:
            raise ValueError(f"Patient not found: {patient.id}")
        self.patients[patient.id] = patient
        return patient

    def delete(self, patient_id: str) -> None:
        self.patients.pop(patient_id, None)
