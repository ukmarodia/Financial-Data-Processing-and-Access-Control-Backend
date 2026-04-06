


def test_register_user(client):
   
    response = client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test User", "password": "securepass"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@domain.com"
    assert data["role"] == "viewer"  
    assert "id" in data
    assert "hashed_password" not in data  


def test_register_duplicate_email(client):
   
    payload = {"email": "test@domain.com", "full_name": "Test User", "password": "securepass"}
    client.post("/api/auth/register", json=payload)

    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["error_code"] == "BadRequestError"


def test_register_invalid_email_format(client):
    
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "full_name": "Test", "password": "securepass"}
    )
    assert response.status_code == 422


def test_register_password_too_short(client):
    
    response = client.post(
        "/api/auth/register",
        json={"email": "test@domain.com", "full_name": "Test", "password": "abc"}
    )
    assert response.status_code == 422


def test_login_success(client):
   
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
   
    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@domain.com", "password": "securepass"}
    )
    assert response.status_code == 401


def test_me_endpoint_returns_own_profile(client):
   
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
