from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreatePatientCommand:
    user_id: str | None
    tipo_documento: str
    numero_documento: str
    full_name: str
    fecha_nacimiento: date
    telefono: str | None = None
    email: str | None = None
    direccion: str | None = None
