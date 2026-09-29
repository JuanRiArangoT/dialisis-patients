from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CreatePatientRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str | None = None
    tipo_documento: str = Field(..., min_length=1, max_length=20, examples=["CC"])
    numero_documento: str = Field(
        ..., min_length=1, max_length=50, examples=["1234567890"]
    )
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Juan Pérez"])
    fecha_nacimiento: date
    telefono: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=255)

    @field_validator("fecha_nacimiento")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        today = datetime.now(tz=UTC).date()
        if value > today:
            raise ValueError("La fecha de nacimiento no puede ser una fecha futura")
        return value


class UpdatePatientRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str | None = None
    tipo_documento: str = Field(..., min_length=1, max_length=20, examples=["CC"])
    numero_documento: str = Field(
        ..., min_length=1, max_length=50, examples=["1234567890"]
    )
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Juan Pérez"])
    fecha_nacimiento: date
    telefono: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=255)
    is_active: bool = True

    @field_validator("fecha_nacimiento")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        today = datetime.now(tz=UTC).date()
        if value > today:
            raise ValueError("La fecha de nacimiento no puede ser una fecha futura")
        return value


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
