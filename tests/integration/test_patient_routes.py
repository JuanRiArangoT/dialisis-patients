from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "patients-microservice",
        "database": "connected",
    }


def test_health_check_database_unhealthy(client: TestClient) -> None:
    from fastapi import HTTPException

    from patients.adapters.inbound.http.dependencies.database import check_db_health
    from patients.main import app

    def broken_db() -> str:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "patients-microservice",
                "database": "disconnected",
            },
        )

    app.dependency_overrides[check_db_health] = broken_db
    try:
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json()["detail"]["database"] == "disconnected"
    finally:
        app.dependency_overrides[check_db_health] = lambda: "connected"


def test_create_patient_success(client: TestClient) -> None:
    payload = {
        "tipo_documento": "CC",
        "numero_documento": "100200300",
        "full_name": "Ana Maria Ramirez",
        "fecha_nacimiento": "1990-04-15",
        "telefono": "3101234567",
        "email": "ana.ramirez@example.com",
        "direccion": "Carrera 15 # 45-67",
    }

    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "patient_id" in data
    assert data["full_name"] == "Ana Maria Ramirez"
    assert data["numero_documento"] == "100200300"
    assert data["email"] == "ana.ramirez@example.com"
    assert data["is_active"] is True


def test_create_patient_future_birth_date_fails_validation(client: TestClient) -> None:
    payload = {
        "tipo_documento": "CC",
        "numero_documento": "999888777",
        "full_name": "Viajero del Tiempo",
        "fecha_nacimiento": "2099-01-01",
    }

    response = client.post("/patients", json=payload)
    assert response.status_code == 422
    assert "fecha de nacimiento no puede ser una fecha futura" in response.text


def test_create_patient_blank_fields_fails_validation(client: TestClient) -> None:
    payload = {
        "tipo_documento": "",
        "numero_documento": "   ",
        "full_name": "",
        "fecha_nacimiento": "1990-01-01",
    }

    response = client.post("/patients", json=payload)
    assert response.status_code == 422


def test_create_patient_duplicate_document_returns_409(client: TestClient) -> None:
    payload = {
        "tipo_documento": "CC",
        "numero_documento": "DUPLICADO123",
        "full_name": "Paciente Original",
        "fecha_nacimiento": "1988-08-08",
    }

    res1 = client.post("/patients", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/patients", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_list_patients_flow(client: TestClient) -> None:
    initial_res = client.get("/patients")
    assert initial_res.status_code == 200
    assert initial_res.json() == {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "total_pages": 0,
    }

    client.post(
        "/patients",
        json={
            "tipo_documento": "CC",
            "numero_documento": "111",
            "full_name": "Beto Perez",
            "fecha_nacimiento": "1980-01-01",
        },
    )
    client.post(
        "/patients",
        json={
            "tipo_documento": "CC",
            "numero_documento": "222",
            "full_name": "Alvaro Lopez",
            "fecha_nacimiento": "1982-02-02",
        },
    )

    list_res = client.get("/patients")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["total_pages"] == 1
    assert len(data["items"]) == 2
    assert data["items"][0]["full_name"] == "Alvaro Lopez"
    assert data["items"][1]["full_name"] == "Beto Perez"


def test_list_patients_with_search_and_pagination(client: TestClient) -> None:
    for i in range(1, 6):
        client.post(
            "/patients",
            json={
                "tipo_documento": "CC",
                "numero_documento": f"ID-{i}",
                "full_name": f"Paciente {i}",
                "fecha_nacimiento": "1985-05-05",
            },
        )

    # Test page_size=2
    res_page_1 = client.get("/patients?page=1&page_size=2")
    assert res_page_1.status_code == 200
    data_1 = res_page_1.json()
    assert data_1["total"] == 5
    assert data_1["total_pages"] == 3
    assert len(data_1["items"]) == 2

    # Test search by document
    res_search = client.get("/patients?search=ID-3")
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert data_search["total"] == 1
    assert data_search["items"][0]["numero_documento"] == "ID-3"


def test_get_patient_by_id(client: TestClient) -> None:
    create_res = client.post(
        "/patients",
        json={
            "tipo_documento": "CC",
            "numero_documento": "333444",
            "full_name": "Sofia Vergara",
            "fecha_nacimiento": "1972-07-10",
        },
    )
    patient_id = create_res.json()["patient_id"]

    get_res = client.get(f"/patients/{patient_id}")
    assert get_res.status_code == 200
    assert get_res.json()["full_name"] == "Sofia Vergara"


def test_get_patient_not_found(client: TestClient) -> None:
    response = client.get("/patients/non-existent-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Patient not found: non-existent-id"}


def test_update_patient_success(client: TestClient) -> None:
    create_res = client.post(
        "/patients",
        json={
            "tipo_documento": "CC",
            "numero_documento": "777777",
            "full_name": "Nombre Anterior",
            "fecha_nacimiento": "1995-03-20",
        },
    )
    patient_id = create_res.json()["patient_id"]

    update_payload = {
        "tipo_documento": "CC",
        "numero_documento": "777777",
        "full_name": "Nombre Corregido",
        "fecha_nacimiento": "1995-03-20",
        "telefono": "3005555555",
        "is_active": True,
    }

    put_res = client.put(f"/patients/{patient_id}", json=update_payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["full_name"] == "Nombre Corregido"
    assert data["telefono"] == "3005555555"


def test_update_patient_not_found(client: TestClient) -> None:
    update_payload = {
        "tipo_documento": "CC",
        "numero_documento": "12345",
        "full_name": "Cualquier Nombre",
        "fecha_nacimiento": "1995-03-20",
    }

    put_res = client.put("/patients/inexistente", json=update_payload)
    assert put_res.status_code == 404


def test_delete_patient_flow(client: TestClient) -> None:
    create_res = client.post(
        "/patients",
        json={
            "tipo_documento": "TI",
            "numero_documento": "888999",
            "full_name": "Paciente Temporal",
            "fecha_nacimiento": "2008-11-15",
        },
    )
    patient_id = create_res.json()["patient_id"]

    del_res = client.delete(f"/patients/{patient_id}")
    assert del_res.status_code == 204

    # Verify patient is marked inactive (soft deleted), not physically purged
    get_res = client.get(f"/patients/{patient_id}")
    assert get_res.status_code == 200
    assert get_res.json()["is_active"] is False


def test_delete_patient_not_found(client: TestClient) -> None:
    del_res = client.delete("/patients/id-fantasma")
    assert del_res.status_code == 404


def test_desactivate_and_reactivate_patient_endpoints(client: TestClient) -> None:
    create_res = client.post(
        "/patients",
        json={
            "tipo_documento": "CC",
            "numero_documento": "55512345",
            "full_name": "Paciente Reactivable",
            "fecha_nacimiento": "1992-06-10",
        },
    )
    patient_id = create_res.json()["patient_id"]
    assert create_res.json()["is_active"] is True

    # Desactivate via PATCH
    deact_res = client.patch(f"/patients/{patient_id}/desactivate")
    assert deact_res.status_code == 200
    assert deact_res.json()["is_active"] is False

    # Reactivate via PATCH
    react_res = client.patch(f"/patients/{patient_id}/reactivate")
    assert react_res.status_code == 200
    assert react_res.json()["is_active"] is True
