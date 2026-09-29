from fastapi import Request
from fastapi.responses import JSONResponse

from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
    PatientNotFoundApplicationError,
)


def patient_not_found_exception_handler(
    request: Request,
    exc: PatientNotFoundApplicationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


def patient_conflict_exception_handler(
    request: Request,
    exc: PatientConflictApplicationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )
