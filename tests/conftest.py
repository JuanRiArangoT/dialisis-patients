from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from patients.adapters.inbound.http.dependencies.auth0_jwt import (
    get_current_user,
)
from patients.adapters.inbound.http.dependencies.patients import (
    get_patient_repository,
)
from patients.main import app
from tests.unit.fakes.in_memory_patient_repository import InMemoryPatientRepository


@pytest.fixture
def fake_repository() -> InMemoryPatientRepository:
    return InMemoryPatientRepository()


@pytest.fixture
def client(fake_repository: InMemoryPatientRepository) -> Generator[TestClient]:
    app.dependency_overrides[get_patient_repository] = lambda: fake_repository
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "auth0|test-user-id",
        "name": "Test User",
        "email": "test@example.com",
    }

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
