from fastapi import APIRouter, Depends, Response, status

from patients.adapters.inbound.http.dependencies.auth0_jwt import (
    CurrentUser,
)
from patients.adapters.inbound.http.dependencies.authorization import (
    require_permission,
)
from patients.adapters.inbound.http.dependencies.patients import (
    get_create_patient_use_case,
    get_delete_patient_use_case,
    get_get_patient_use_case,
    get_list_patients_use_case,
    get_update_patient_use_case,
)
from patients.adapters.inbound.http.schemas.patient import (
    CreatePatientRequest,
    PatientResponse,
    UpdatePatientRequest,
)
from patients.application.dtos.create_patient import CreatePatientCommand
from patients.application.dtos.update_patient import UpdatePatientCommand
from patients.application.use_cases.create_patient import CreatePatientUseCase
from patients.application.use_cases.delete_patient import DeletePatientUseCase
from patients.application.use_cases.get_patient import GetPatientUseCase
from patients.application.use_cases.list_patients import ListPatientsUseCase
from patients.application.use_cases.update_patient import UpdatePatientUseCase

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    request: CreatePatientRequest,
    current_user: CurrentUser,
    use_case: CreatePatientUseCase = Depends(
        get_create_patient_use_case,
    ),
) -> PatientResponse:
    command = CreatePatientCommand(
        user_id=request.user_id,
        tipo_documento=request.tipo_documento,
        numero_documento=request.numero_documento,
        full_name=request.full_name,
        fecha_nacimiento=request.fecha_nacimiento,
        telefono=request.telefono,
        email=request.email,
        direccion=request.direccion,
    )

    patient = use_case.execute(command)

    return PatientResponse.model_validate(patient)


@router.get(
    "",
    response_model=list[PatientResponse],
    dependencies=[Depends(require_permission("patients.read"))],
)
def list_patients(
    current_user: CurrentUser,
    use_case: ListPatientsUseCase = Depends(
        get_list_patients_use_case,
    ),
) -> list[PatientResponse]:
    patients = use_case.execute()

    return [PatientResponse.model_validate(patient) for patient in patients]


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: str,
    current_user: CurrentUser,
    use_case: GetPatientUseCase = Depends(
        get_get_patient_use_case,
    ),
) -> PatientResponse:
    patient = use_case.execute(patient_id)

    return PatientResponse.model_validate(patient)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient(
    patient_id: str,
    request: UpdatePatientRequest,
    current_user: CurrentUser,
    use_case: UpdatePatientUseCase = Depends(
        get_update_patient_use_case,
    ),
) -> PatientResponse:
    command = UpdatePatientCommand(
        user_id=request.user_id,
        tipo_documento=request.tipo_documento,
        numero_documento=request.numero_documento,
        full_name=request.full_name,
        fecha_nacimiento=request.fecha_nacimiento,
        telefono=request.telefono,
        email=request.email,
        direccion=request.direccion,
        is_active=request.is_active,
    )

    patient = use_case.execute(
        patient_id,
        command,
    )

    return PatientResponse.model_validate(patient)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: str,
    current_user: CurrentUser,
    use_case: DeletePatientUseCase = Depends(
        get_delete_patient_use_case,
    ),
) -> Response:
    use_case.execute(patient_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
