from uuid import uuid4

from fastapi.testclient import TestClient


def unique_value(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:8]}".upper()


def create_user(client: TestClient, *, name: str = "Test User") -> dict:
    response = client.post(
        "/api/v1/users",
        json={"name": name, "institutional_id": unique_value("UCE")},
    )
    assert response.status_code == 201
    return response.json()


def create_vehicle(client: TestClient, user_id: int) -> dict:
    response = client.post(
        "/api/v1/vehicles",
        json={"user_id": user_id, "plate": unique_value("P")},
    )
    assert response.status_code == 201
    return response.json()


def create_permission(
    client: TestClient, user_id: int, vehicle_id: int, *, active: bool = True
) -> dict:
    response = client.post(
        "/api/v1/permissions",
        json={"user_id": user_id, "vehicle_id": vehicle_id, "active": active},
    )
    assert response.status_code == 201
    return response.json()


def authorize(client: TestClient, user_id: int, plate: str) -> dict:
    response = client.post(
        "/api/v1/access/authorize",
        json={
            "user_id": user_id,
            "detected_plate": plate,
            "event_type": "ENTRY",
            "face_score": 0.95,
            "plate_score": 0.97,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_health_returns_200(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_user(client: TestClient):
    institutional_id = unique_value("uce")
    response = client.post(
        "/api/v1/users",
        json={"name": "  Ana Pérez  ", "institutional_id": institutional_id.lower()},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Ana Pérez"
    assert response.json()["institutional_id"] == institutional_id


def test_create_vehicle(client: TestClient):
    user = create_user(client)
    response = client.post(
        "/api/v1/vehicles",
        json={"user_id": user["id"], "plate": " pbc 1234 ", "brand": "Toyota"},
    )
    assert response.status_code == 201
    assert response.json()["plate"] == "PBC1234"
    assert response.json()["user_id"] == user["id"]


def test_create_permission(client: TestClient):
    user = create_user(client)
    vehicle = create_vehicle(client, user["id"])
    permission = create_permission(client, user["id"], vehicle["id"])
    assert permission["active"] is True
    assert permission["vehicle_id"] == vehicle["id"]


def test_authorization_is_authorized_and_event_is_saved(client: TestClient):
    user = create_user(client)
    vehicle = create_vehicle(client, user["id"])
    create_permission(client, user["id"], vehicle["id"])

    result = authorize(client, user["id"], vehicle["plate"])
    assert result["decision"] == "AUTHORIZED"
    assert result["vehicle_id"] == vehicle["id"]

    events = client.get("/api/v1/access-events")
    assert events.status_code == 200
    assert any(
        event["decision"] == "AUTHORIZED"
        and event["vehicle_id"] == vehicle["id"]
        for event in events.json()
    )


def test_vehicle_owned_by_another_user_requires_review(client: TestClient):
    recognized_user = create_user(client, name="Recognized User")
    owner = create_user(client, name="Vehicle Owner")
    vehicle = create_vehicle(client, owner["id"])

    result = authorize(client, recognized_user["id"], vehicle["plate"])
    assert result["decision"] == "REVIEW"


def test_inactive_permission_is_rejected(client: TestClient):
    user = create_user(client)
    vehicle = create_vehicle(client, user["id"])
    create_permission(client, user["id"], vehicle["id"], active=False)

    result = authorize(client, user["id"], vehicle["plate"])
    assert result["decision"] == "REJECTED"
    assert "inactive" in result["reason"].lower()


def test_unknown_user_is_rejected(client: TestClient):
    result = authorize(client, 2_000_000_000, unique_value("P"))
    assert result["decision"] == "REJECTED"
    assert result["vehicle_id"] is None


def test_unregistered_plate_is_rejected(client: TestClient):
    user = create_user(client)
    result = authorize(client, user["id"], unique_value("P"))
    assert result["decision"] == "REJECTED"
    assert "not registered" in result["reason"].lower()


def test_expired_permission_is_rejected(client: TestClient):
    user = create_user(client)
    vehicle = create_vehicle(client, user["id"])
    response = client.post(
        "/api/v1/permissions",
        json={
            "user_id": user["id"],
            "vehicle_id": vehicle["id"],
            "active": True,
            "valid_from": "2020-01-01T00:00:00Z",
            "valid_to": "2020-12-31T23:59:59Z",
        },
    )
    assert response.status_code == 201
    result = authorize(client, user["id"], vehicle["plate"])
    assert result["decision"] == "REJECTED"
    assert "expired" in result["reason"].lower()


def test_duplicates_return_conflict(client: TestClient):
    institutional_id = unique_value("UCE")
    payload = {"name": "Duplicate Test", "institutional_id": institutional_id}
    first_user = client.post("/api/v1/users", json=payload)
    assert first_user.status_code == 201
    assert client.post("/api/v1/users", json=payload).status_code == 409

    user_id = first_user.json()["id"]
    plate = unique_value("P")
    vehicle_payload = {"user_id": user_id, "plate": plate}
    first_vehicle = client.post("/api/v1/vehicles", json=vehicle_payload)
    assert first_vehicle.status_code == 201
    assert client.post("/api/v1/vehicles", json=vehicle_payload).status_code == 409

    permission_payload = {
        "user_id": user_id,
        "vehicle_id": first_vehicle.json()["id"],
    }
    assert client.post("/api/v1/permissions", json=permission_payload).status_code == 201
    assert client.post("/api/v1/permissions", json=permission_payload).status_code == 409


def test_invalid_authorization_payload_returns_422(client: TestClient):
    response = client.post(
        "/api/v1/access/authorize",
        json={
            "user_id": 1,
            "detected_plate": "PBC1234",
            "event_type": "INVALID",
            "face_score": 1.5,
        },
    )
    assert response.status_code == 422
