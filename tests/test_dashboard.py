
from app.models.user import UserRole
from app.services.user_service import UserService


def _register_and_get_id(client, db_session, email, name, password, role=None) -> int:
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": name, "password": password}
    )
    user_id = resp.json()["id"]
    if role:
        UserService.change_role(db_session, user_id, role)
    return user_id


def _get_token(client, email, password) -> dict:
    resp = client.post("/api/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


INCOME_RECORD = {"amount": 1000.0, "type": "income", "category": "salary", "date": "2024-06-01"}
EXPENSE_RECORD = {"amount": 200.0, "type": "expense", "category": "rent", "date": "2024-06-15"}


def test_viewer_can_access_dashboard(client, db_session):

    _register_and_get_id(client, db_session, "viewer@test.com", "Viewer", "viewerpass")
    headers = _get_token(client, "viewer@test.com", "viewerpass")

    assert client.get("/api/dashboard/summary", headers=headers).status_code == 200
    assert client.get("/api/dashboard/trends", headers=headers).status_code == 200
    assert client.get("/api/dashboard/category-breakdown", headers=headers).status_code == 200
    assert client.get("/api/dashboard/recent", headers=headers).status_code == 200


def test_analyst_can_access_dashboard(client, db_session):
   
    _register_and_get_id(client, db_session, "analyst@test.com", "Analyst", "analystpass", UserRole.ANALYST)
    headers = _get_token(client, "analyst@test.com", "analystpass")

    assert client.get("/api/dashboard/summary", headers=headers).status_code == 200
    assert client.get("/api/dashboard/trends", headers=headers).status_code == 200
    assert client.get("/api/dashboard/category-breakdown", headers=headers).status_code == 200
    assert client.get("/api/dashboard/recent", headers=headers).status_code == 200


def test_summary_math_is_correct(client, db_session):
    
    admin_id = _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    admin_headers = _get_token(client, "admin@test.com", "adminpass")
    analyst_headers = _get_token(client, "admin@test.com", "adminpass")  

    
    client.post("/api/records", json=INCOME_RECORD, headers=admin_headers)
    client.post("/api/records", json=EXPENSE_RECORD, headers=admin_headers)

    resp = client.get("/api/dashboard/summary", headers=analyst_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_income"] == 1000.0
    assert data["total_expenses"] == 200.0
    assert data["net_balance"] == 800.0
    assert data["record_count"] == 2


def test_category_breakdown_groups_correctly(client, db_session):
   
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

   
    client.post("/api/records", json={**INCOME_RECORD, "amount": 500.0, "category": "salary"}, headers=headers)
    client.post("/api/records", json={**INCOME_RECORD, "amount": 300.0, "category": "salary"}, headers=headers)
    
    client.post("/api/records", json={**INCOME_RECORD, "amount": 200.0, "category": "bonus"}, headers=headers)

    resp = client.get("/api/dashboard/category-breakdown", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    income_totals = {item["category"]: item["total"] for item in data["income_by_category"]}
    assert income_totals["salary"] == 800.0
    assert income_totals["bonus"] == 200.0


def test_recent_activity_returns_latest_records(client, db_session):
   
    _register_and_get_id(client, db_session, "admin@test.com", "Admin", "adminpass", UserRole.ADMIN)
    headers = _get_token(client, "admin@test.com", "adminpass")

    for i in range(12):
        client.post("/api/records", json={**INCOME_RECORD, "category": f"cat_{i}"}, headers=headers)

    resp = client.get("/api/dashboard/recent", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 10 
