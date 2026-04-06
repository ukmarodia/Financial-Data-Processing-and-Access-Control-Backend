from app.models.user import UserRole
from app.services.user_service import UserService


def _register_and_get_id(client, db_session, email, name, password, role=None) -> int:
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
    resp = client.post("/api/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.json()}"
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_admin_can_list_users(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    response = client.get("/api/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_analyst_cannot_list_users(client, db_session):
    _register_and_get_id(client, db_session, "analyst@test.com", "Analyst", "analystpass", UserRole.ANALYST)
    headers = _get_token(client, "analyst@test.com", "analystpass")

    response = client.get("/api/users", headers=headers)
    assert response.status_code == 403


def test_admin_can_change_user_role(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    user_id = _register_and_get_id(client, db_session, "user@test.com", "User", "userpass")
    headers = _get_token(client, "admin@test.com", "adminpass")

    response = client.patch(
        f"/api/users/{user_id}/role",
        json={"role": "analyst"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "analyst"


def test_admin_can_deactivate_other_user(client, db_session):
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    user_id = _register_and_get_id(client, db_session, "user@test.com", "User", "userpass")
    headers = _get_token(client, "admin@test.com", "adminpass")

    response = client.patch(
        f"/api/users/{user_id}/status",
        json={"is_active": False},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_admin_cannot_deactivate_self(client, db_session):
    admin_id = _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    response = client.patch(
        f"/api/users/{admin_id}/status",
        json={"is_active": False},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "BadRequestError"
