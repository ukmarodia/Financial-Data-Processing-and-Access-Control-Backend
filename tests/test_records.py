"""
Tests for financial record CRUD operations and RBAC enforcement.

Design note: We avoid relying on hardcoded user IDs by querying the DB
directly for user IDs after registration. This makes tests robust even
if auto-increment behavior changes.
"""
from app.models.user import UserRole
from app.services.user_service import UserService


def _register_and_get_id(client, db_session, email, name, password, role=None) -> int:
    """Helper: register a user and optionally bump their role. Returns their DB id."""
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": name, "password": password}
    )
    assert resp.status_code == 201, f"Registration failed: {resp.json()}"
    user_id = resp.json()["id"]
    if role:
        UserService.change_role(db_session, user_id, role)
    return user_id


def _get_token(client, email, password) -> dict:
    """Helper: login and return Authorization headers."""
    resp = client.post("/api/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.json()}"
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


RECORD_PAYLOAD = {
    "amount": 500.50,
    "type": "income",
    "category": "freelance",
    "date": "2024-05-01",
    "description": "Side project payment"
}


def test_admin_can_create_record(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    response = client.post("/api/records", json=RECORD_PAYLOAD, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 500.50
    assert data["category"] == "freelance"
    assert data["type"] == "income"


def test_viewer_cannot_create_record(client, db_session):
    _register_and_get_id(client, db_session, "viewer@test.com", "Viewer", "viewerpass")
    headers = _get_token(client, "viewer@test.com", "viewerpass")

    response = client.post("/api/records", json=RECORD_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_analyst_cannot_create_record(client, db_session):
    _register_and_get_id(client, db_session, "analyst@test.com", "Analyst", "analystpass", UserRole.ANALYST)
    headers = _get_token(client, "analyst@test.com", "analystpass")

    response = client.post("/api/records", json=RECORD_PAYLOAD, headers=headers)
    assert response.status_code == 403


def test_record_validation_negative_amount(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    bad_payload = {**RECORD_PAYLOAD, "amount": -100}
    response = client.post("/api/records", json=bad_payload, headers=headers)
    assert response.status_code == 422  # Pydantic validation error


def test_admin_can_update_record(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    create_resp = client.post("/api/records", json=RECORD_PAYLOAD, headers=headers)
    record_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/records/{record_id}",
        json={"description": "Updated note"},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "Updated note"


def test_admin_can_soft_delete_record(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    create_resp = client.post("/api/records", json=RECORD_PAYLOAD, headers=headers)
    record_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/records/{record_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify record is gone from list (soft deleted)
    list_resp = client.get("/api/records", headers=headers)
    ids_in_response = [r["id"] for r in list_resp.json()["items"]]
    assert record_id not in ids_in_response


def test_pagination_works(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    # Create 5 records
    for i in range(5):
        client.post("/api/records", json={**RECORD_PAYLOAD, "category": f"category_{i}"}, headers=headers)

    resp = client.get("/api/records?page=1&per_page=3", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3
    assert data["pages"] == 2


def test_unauthenticated_request_returns_401(client, db_session):
    response = client.get("/api/records")
    assert response.status_code == 401
