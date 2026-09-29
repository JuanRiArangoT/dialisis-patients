from patients.application.dtos.patient_output import PatientOutputDTO
from patients.application.ports.patient_repository import PatientRepositoryPort


class ListPatientsUseCase:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
    ) -> None:
        self._patient_repository = patient_repository

    def execute(self) -> list[PatientOutputDTO]:
        patients = self._patient_repository.get_all()

        return [
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
