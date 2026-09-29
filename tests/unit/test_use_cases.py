from datetime import date

import pytest

from patients.application.dtos.create_patient import CreatePatientCommand
from patients.application.dtos.list_patients_query import ListPatientsQuery
from patients.application.dtos.update_patient import UpdatePatientCommand
from patients.application.exceptions.patient_exceptions import (
    PatientConflictApplicationError,
    PatientNotFoundApplicationError,
)
from patients.application.use_cases.create_patient import CreatePatientUseCase
from patients.application.use_cases.delete_patient import DeletePatientUseCase
from patients.application.use_cases.desactivate_patient import (
    DesactivatePatientUseCase,
)
from patients.application.use_cases.get_patient import GetPatientUseCase
from patients.application.use_cases.list_patients import ListPatientsUseCase
from patients.application.use_cases.reactivate_patient import (
    ReactivatePatientUseCase,
)
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

    empty_result = use_case.execute()
    assert empty_result.items == []
    assert empty_result.total == 0
    assert empty_result.total_pages == 0

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
    assert results.total == 2
    assert results.total_pages == 1
    assert len(results.items) == 2
    assert results.items[0].full_name == "Andres Perez"
    assert results.items[1].full_name == "Berta Gomez"


def test_list_patients_pagination_and_search(
    repository: InMemoryPatientRepository,
) -> None:
    for i in range(1, 11):
        repository.create(
            Patient(
                id=f"p-{i}",
                user_id=None,
                tipo_documento="CC",
                numero_documento=f"DOC-{i:03d}",
                full_name=f"Paciente {i:02d}",
                fecha_nacimiento=date(1980, 1, 1),
                is_active=(i % 2 == 0),
            )
        )

    use_case = ListPatientsUseCase(repository)

    # Page 1 with page_size=4
    page_1 = use_case.execute(ListPatientsQuery(page=1, page_size=4))
    assert page_1.total == 10
    assert page_1.total_pages == 3
    assert len(page_1.items) == 4
    assert page_1.items[0].full_name == "Paciente 01"

    # Page 3 with page_size=4 (should have 2 items remaining)
    page_3 = use_case.execute(ListPatientsQuery(page=3, page_size=4))
    assert len(page_3.items) == 2

    # Filter search by document
    search_doc = use_case.execute(ListPatientsQuery(search="005"))
    assert search_doc.total == 1
    assert search_doc.items[0].numero_documento == "DOC-005"

    # Filter by is_active=True (should find 5 active patients)
    active_result = use_case.execute(ListPatientsQuery(is_active=True))
    assert active_result.total == 5
    assert all(p.is_active for p in active_result.items)


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


def test_delete_patient_success_performs_soft_delete(
    repository: InMemoryPatientRepository,
) -> None:
    repository.create(
        Patient(
            id="pat-to-del",
            user_id=None,
            tipo_documento="CC",
            numero_documento="12345",
            full_name="A Borrar",
            fecha_nacimiento=date(1990, 5, 5),
            is_active=True,
        )
    )

    use_case = DeletePatientUseCase(repository)
    use_case.execute("pat-to-del")

    patient = repository.get_by_id("pat-to-del")
    assert patient is not None
    assert patient.is_active is False


def test_delete_patient_not_found(repository: InMemoryPatientRepository) -> None:
    use_case = DeletePatientUseCase(repository)

    with pytest.raises(PatientNotFoundApplicationError):
        use_case.execute("non-existent-id")


def test_desactivate_patient_success(repository: InMemoryPatientRepository) -> None:
    repository.create(
        Patient(
            id="pat-deact",
            user_id=None,
            tipo_documento="CC",
            numero_documento="998877",
            full_name="Paciente Activo",
            fecha_nacimiento=date(1985, 3, 10),
            is_active=True,
        )
    )

    use_case = DesactivatePatientUseCase(repository)
    result = use_case.execute("pat-deact")

    assert result.is_active is False
    persisted = repository.get_by_id("pat-deact")
    assert persisted is not None
    assert persisted.is_active is False


def test_desactivate_patient_already_inactive(
    repository: InMemoryPatientRepository,
) -> None:
    repository.create(
        Patient(
            id="pat-already-inactive",
            user_id=None,
            tipo_documento="CC",
            numero_documento="554433",
            full_name="Paciente Inactivo",
            fecha_nacimiento=date(1985, 3, 10),
            is_active=False,
        )
    )

    use_case = DesactivatePatientUseCase(repository)
    result = use_case.execute("pat-already-inactive")

    assert result.is_active is False


def test_desactivate_patient_not_found(repository: InMemoryPatientRepository) -> None:
    use_case = DesactivatePatientUseCase(repository)

    with pytest.raises(PatientNotFoundApplicationError):
        use_case.execute("non-existent")


def test_reactivate_patient_success(repository: InMemoryPatientRepository) -> None:
    repository.create(
        Patient(
            id="pat-react",
            user_id=None,
            tipo_documento="CC",
            numero_documento="112233",
            full_name="Paciente Retirado",
            fecha_nacimiento=date(1980, 7, 20),
            is_active=False,
        )
    )

    use_case = ReactivatePatientUseCase(repository)
    result = use_case.execute("pat-react")

    assert result.is_active is True
    persisted = repository.get_by_id("pat-react")
    assert persisted is not None
    assert persisted.is_active is True


def test_reactivate_patient_already_active(
    repository: InMemoryPatientRepository,
) -> None:
    repository.create(
        Patient(
            id="pat-already-active",
            user_id=None,
            tipo_documento="CC",
            numero_documento="445566",
            full_name="Paciente Ya Activo",
            fecha_nacimiento=date(1980, 7, 20),
            is_active=True,
        )
    )

    use_case = ReactivatePatientUseCase(repository)
    result = use_case.execute("pat-already-active")

    assert result.is_active is True


def test_reactivate_patient_not_found(repository: InMemoryPatientRepository) -> None:
    use_case = ReactivatePatientUseCase(repository)

    with pytest.raises(PatientNotFoundApplicationError):
        use_case.execute("non-existent")
