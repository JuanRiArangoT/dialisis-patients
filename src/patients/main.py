from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from patients.adapters.inbound.http.dependencies.database import check_db_health
from patients.adapters.inbound.http.exceptions.patient_exceptions import (
    patient_conflict_exception_handler,
    patient_not_found_exception_handler,
)
from patients.adapters.inbound.http.routes.patients import (
    router as patients_router,
)
from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
    PatientNotFoundApplicationError,
)
from patients.infrastructure.config.settings import settings

app = FastAPI(
    title="Servicio de Pacientes - Diálisis",
    description="Microservicio de pacientes con arquitectura hexagonal",
    version="1.0.0",
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients_router)


@app.get("/health")
def health(db_status: str = Depends(check_db_health)) -> dict[str, str]:
    return {
        "status": "ok",
        "service": "patients-microservice",
        "database": db_status,
    }


app.add_exception_handler(
    PatientNotFoundApplicationError,
    patient_not_found_exception_handler,
)

app.add_exception_handler(
    PatientConflictApplicationError,
    patient_conflict_exception_handler,
)
