# Finance Dashboard Backend

Backend assignment submission for a finance dashboard system with role-based access control, financial record APIs, and summary analytics.

## Stack

- Framework: FastAPI
- ORM: SQLAlchemy 2.x
- Database: SQLite (default, configurable via `DATABASE_URL`)
- Auth: JWT (`python-jose`) + password hashing (`passlib/bcrypt`)
- Validation: Pydantic v2
- Tests: pytest + FastAPI TestClient

## Features

- User registration/login and profile endpoint
- Admin user management (list users, change role, activate/deactivate)
- Financial records CRUD with soft delete
- Filtering, pagination, and text search for records
- Dashboard summary endpoints (totals, category breakdown, trends, recent activity)
- Role-based backend access control
- Input validation + consistent error responses

## Role Model

- Viewer: dashboard read access only
- Analyst: can read records + dashboard insights
- Admin: full access (records + user management)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload
```

Open Swagger: http://localhost:8000/docs

## Environment

`.env.example` includes:

- `SECRET_KEY`
- `DATABASE_URL`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALGORITHM`

## API Overview

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Users (Admin only)

- `GET /api/users`
- `GET /api/users/{user_id}`
- `PATCH /api/users/{user_id}/role`
- `PATCH /api/users/{user_id}/status`

### Records

- `GET /api/records` (Admin, Analyst)
- `GET /api/records/{record_id}` (Admin, Analyst)
- `POST /api/records` (Admin)
- `PUT /api/records/{record_id}` (Admin)
- `DELETE /api/records/{record_id}` (Admin, soft delete)

Filters on `GET /api/records`:

- `type`
- `category`
- `date_from`
- `date_to`
- `q` (category/notes search)
- `page`, `per_page`

### Dashboard

- `GET /api/dashboard/summary` (Viewer, Analyst, Admin)
- `GET /api/dashboard/category-breakdown` (Viewer, Analyst, Admin)
- `GET /api/dashboard/trends` (Viewer, Analyst, Admin)
- `GET /api/dashboard/recent` (Viewer, Analyst, Admin)

## Requirement Mapping

### 1. User and Role Management

- User creation: `POST /api/auth/register`
- Role assignment + status management: users endpoints under `/api/users/*`
- Role enforcement: `app/api/deps.py` (`require_role` dependency)

### 2. Financial Records Management

- Create/read/update/delete: `/api/records` endpoints
- Fields modeled in `app/models/record.py`
- Filtering/pagination/search in records list endpoint and record service

### 3. Dashboard Summary APIs

- Totals: `/api/dashboard/summary`
- Category totals: `/api/dashboard/category-breakdown`
- Trends: `/api/dashboard/trends`
- Recent activity: `/api/dashboard/recent`

### 4. Access Control Logic

- Route-level RBAC via `require_role`
- Policies:
  - Viewer cannot access records CRUD
  - Analyst can read records and dashboard
  - Admin can manage records and users

### 5. Validation and Error Handling

- Pydantic schemas validate request data
- Domain-specific exceptions in `app/exceptions.py`
- Consistent JSON error payload via FastAPI exception handlers

### 6. Data Persistence

- SQLite default database through SQLAlchemy
- `DATABASE_URL` can be changed to another SQL database URI

## Testing

Run:

```bash
pytest -v tests/
```

Current tests covers:

- Auth flows
- Role restrictions
- Records behavior (validation, pagination, soft delete)
- Dashboard aggregations
- Admin user-management actions

## Assumptions and Tradeoffs

- Soft delete is used for records (`is_deleted`) to preserve history.
- `Float` is used for amounts for assignment simplicity; in production, decimal types are preferred for financial precision.
- Schema setup uses `create_all()` for quick setup; migrations (Alembic) can be added for production workflows.
