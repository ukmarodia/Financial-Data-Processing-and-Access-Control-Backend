"""
Tests for authentication endpoints: registration, login, duplicate detection, bad credentials.
"""


def test_register_user(client):
    """Successful registration returns the user profile with default Viewer role."""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test User", "password": "securepass"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@domain.com"
    assert data["role"] == "viewer"  # All registrations default to viewer
    assert "id" in data
    assert "hashed_password" not in data  # Password must never be exposed


def test_register_duplicate_email(client):
    """Registering with an already-used email returns 400 with a clear error."""
    payload = {"email": "test@domain.com", "full_name": "Test User", "password": "securepass"}
    client.post("/api/auth/register", json=payload)

    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["error_code"] == "BadRequestError"


def test_register_invalid_email_format(client):
    """Pydantic should reject a badly formatted email before it hits the DB."""
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "full_name": "Test", "password": "securepass"}
    )
    assert response.status_code == 422


def test_register_password_too_short(client):
    """Passwords shorter than 6 characters should be rejected."""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test", "password": "abc"}
    )
    assert response.status_code == 422


def test_login_success(client):
    """Successful login returns a bearer token."""
    client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test", "password": "securepass"}
    )

    response = client.post(
        "/api/auth/login",
        data={"username": "test@domain.com", "password": "securepass"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Wrong password returns 401 with a consistent error message."""
    client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test", "password": "securepass"}
    )

    response = client.post(
        "/api/auth/login",
        data={"username": "test@domain.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "UnauthorizedError"


def test_login_nonexistent_user(client):
    """Login with an email that doesn't exist returns 401 (not 404, to prevent enumeration)."""
    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@domain.com", "password": "securepass"}
    )
    assert response.status_code == 401


def test_me_endpoint_returns_own_profile(client):
    """GET /auth/me returns the authenticated user's profile."""
    client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test User", "password": "securepass"}
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "test@domain.com", "password": "securepass"}
    )
    token = login_resp.json()["access_token"]

    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test@domain.com"
