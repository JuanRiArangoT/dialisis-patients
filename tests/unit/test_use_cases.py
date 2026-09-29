from datetime import date

import pytest

from patients.application.dtos.create_patient import CreatePatientCommand
from patients.application.dtos.update_patient import UpdatePatientCommand
from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
    PatientNotFoundApplicationError,
)
from patients.application.use_cases.create_patient import CreatePatientUseCase
from patients.application.use_cases.delete_patient import DeletePatientUseCase
from patients.application.use_cases.get_patient import GetPatientUseCase
from patients.application.use_cases.list_patients import ListPatientsUseCase
from patients.application.use_cases.update_patient import UpdatePatientUseCase
from patients.domain.entities.patient import Patient
from tests.unit.fakes.in_memory_patient_repository import InMemoryPatientRepository


@pytest.fixture
def repository() -> InMemoryPatientRepository:
    return InMemoryPatientRepository()


def test_create_patient_success(repository: InMemoryPatientRepository) -> None:
    use_case = CreatePatientUseCase(repository)
    command = CreatePatientCommand(
        user_id="user-123",
        tipo_documento="CC",
        numero_documento="1098765432",
        full_name="Carlos Santana",
        fecha_nacimiento=date(1985, 5, 20),
        telefono="3001234567",
        email="carlos@example.com",
        direccion="Calle 10 # 5-20",
    )

    result = use_case.execute(command)

    assert result.patient_id is not None
    assert result.full_name == "Carlos Santana"
    assert result.numero_documento == "1098765432"
    assert result.user_id == "user-123"
    assert result.is_active is True

    # Verify persisted in repository
    persisted = repository.get_by_id(result.patient_id)
    assert persisted is not None
    assert persisted.full_name == "Carlos Santana"


def test_create_patient_duplicate_document_raises_conflict(
    repository: InMemoryPatientRepository,
) -> None:
    use_case = CreatePatientUseCase(repository)
    command1 = CreatePatientCommand(
        user_id="user-1",
        tipo_documento="CC",
        numero_documento="123456",
        full_name="Paciente Uno",
        fecha_nacimiento=date(1990, 1, 1),
    )
    use_case.execute(command1)

    command2 = CreatePatientCommand(
        user_id="user-2",
        tipo_documento="CC",
        numero_documento="123456",
        full_name="Paciente Dos",
        fecha_nacimiento=date(1992, 2, 2),
    )

    with pytest.raises(
        PatientConflictApplicationError, match="Patient already exists with document"
    ):
        use_case.execute(command2)


def test_create_patient_duplicate_user_id_raises_conflict(
    repository: InMemoryPatientRepository,
) -> None:
    use_case = CreatePatientUseCase(repository)
    command1 = CreatePatientCommand(
        user_id="same-user-id",
        tipo_documento="CC",
        numero_documento="11111",
        full_name="Paciente Uno",
        fecha_nacimiento=date(1990, 1, 1),
    )
    use_case.execute(command1)

    command2 = CreatePatientCommand(
        user_id="same-user-id",
        tipo_documento="CC",
        numero_documento="22222",
        full_name="Paciente Dos",
        fecha_nacimiento=date(1992, 2, 2),
    )

    with pytest.raises(
        PatientConflictApplicationError, match="User already linked to a patient"
    ):
        use_case.execute(command2)


def test_get_patient_success(repository: InMemoryPatientRepository) -> None:
    patient = Patient(
        id="pat-1",
        user_id=None,
        tipo_documento="CC",
        numero_documento="987654",
        full_name="Maria Lopez",
        fecha_nacimiento=date(1975, 12, 10),
    )
    repository.create(patient)

    use_case = GetPatientUseCase(repository)
    result = use_case.execute("pat-1")

    assert result.patient_id == "pat-1"
    assert result.full_name == "Maria Lopez"


def test_get_patient_not_found(repository: InMemoryPatientRepository) -> None:
    use_case = GetPatientUseCase(repository)

    with pytest.raises(
        PatientNotFoundApplicationError, match="Patient not found: non-existent"
    ):
        use_case.execute("non-existent")


def test_list_patients_empty_and_populated(
    repository: InMemoryPatientRepository,
) -> None:
    use_case = ListPatientsUseCase(repository)

    assert use_case.execute() == []

    repository.create(
        Patient(
            id="p-1",
            user_id=None,
            tipo_documento="CC",
            numero_documento="111",
            full_name="Berta Gomez",
            fecha_nacimiento=date(1980, 1, 1),
        )
    )
    repository.create(
        Patient(
            id="p-2",
            user_id=None,
            tipo_documento="CC",
            numero_documento="222",
            full_name="Andres Perez",
            fecha_nacimiento=date(1982, 3, 3),
        )
    )

    results = use_case.execute()
    assert len(results) == 2
    assert results[0].full_name == "Andres Perez"
    assert results[1].full_name == "Berta Gomez"


def test_update_patient_success(repository: InMemoryPatientRepository) -> None:
    patient = Patient(
        id="pat-1",
        user_id="user-1",
        tipo_documento="CC",
        numero_documento="123456",
        full_name="Nombre Inicial",
        fecha_nacimiento=date(1980, 1, 1),
        telefono="3000000000",
    )
    repository.create(patient)

    use_case = UpdatePatientUseCase(repository)
    update_cmd = UpdatePatientCommand(
        user_id="user-1",
        tipo_documento="CC",
        numero_documento="123456",
        full_name="Nombre Actualizado",
        fecha_nacimiento=date(1980, 1, 1),
        telefono="3119999999",
        is_active=True,
    )

    updated = use_case.execute("pat-1", update_cmd)

    assert updated.full_name == "Nombre Actualizado"
    assert updated.telefono == "3119999999"


def test_update_patient_not_found(repository: InMemoryPatientRepository) -> None:
    use_case = UpdatePatientUseCase(repository)
    update_cmd = UpdatePatientCommand(
        user_id=None,
        tipo_documento="CC",
        numero_documento="123456",
        full_name="Nombre",
        fecha_nacimiento=date(1980, 1, 1),
    )

    with pytest.raises(PatientNotFoundApplicationError):
        use_case.execute("pat-999", update_cmd)


def test_update_patient_conflict_with_another_patient_document(
    repository: InMemoryPatientRepository,
) -> None:
    repository.create(
        Patient(
            id="p-1",
            user_id=None,
            tipo_documento="CC",
            numero_documento="DOC-1",
            full_name="Paciente Uno",
            fecha_nacimiento=date(1980, 1, 1),
        )
    )
    repository.create(
        Patient(
            id="p-2",
            user_id=None,
            tipo_documento="CC",
            numero_documento="DOC-2",
            full_name="Paciente Dos",
            fecha_nacimiento=date(1985, 2, 2),
        )
    )

    use_case = UpdatePatientUseCase(repository)
    # Attempt to change p-2's document to DOC-1
    update_cmd = UpdatePatientCommand(
        user_id=None,
        tipo_documento="CC",
        numero_documento="DOC-1",
        full_name="Paciente Dos Modificado",
        fecha_nacimiento=date(1985, 2, 2),
    )

    with pytest.raises(
        PatientConflictApplicationError, match="Document is already associated"
    ):
        use_case.execute("p-2", update_cmd)


def test_delete_patient_success(repository: InMemoryPatientRepository) -> None:
    repository.create(
        Patient(
            id="pat-to-del",
            user_id=None,
            tipo_documento="CC",
            numero_documento="12345",
            full_name="A Borrar",
            fecha_nacimiento=date(1990, 5, 5),
        )
    )

    use_case = DeletePatientUseCase(repository)
    use_case.execute("pat-to-del")

    assert repository.get_by_id("pat-to-del") is None


def test_delete_patient_not_found(repository: InMemoryPatientRepository) -> None:
    use_case = DeletePatientUseCase(repository)

    with pytest.raises(PatientNotFoundApplicationError):
        use_case.execute("non-existent-id")
