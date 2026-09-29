from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PatientOutputDTO:
    patient_id: str
    user_id: str | None
    tipo_documento: str
    numero_documento: str
    full_name: str
    fecha_nacimiento: date
    telefono: str | None
    email: str | None
    direccion: str | None
    is_active: bool


@dataclass(frozen=True)
class PaginatedPatientsOutputDTO:
    items: list[PatientOutputDTO]
    total: int
    page: int
    page_size: int
    total_pages: int
