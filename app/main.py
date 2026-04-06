import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

# Models must be imported before create_all() so SQLAlchemy discovers their table definitions.
# Explicit imports here guarantee all tables are registered with the metadata.
import app.models.user  # noqa: F401
import app.models.record  # noqa: F401

from app.api.routes import auth, users, records, dashboard
from app.exceptions import NotFoundError, ForbiddenError, BadRequestError, UnauthorizedError

# Create all tables at startup (idempotent — skips tables that already exist)
Base.metadata.create_all(bind=engine)

tags_metadata = [
    {"name": "Auth", "description": "Operations for logging in and registering users."},
    {"name": "Users", "description": "Admin tools for managing user status and roles."},
    {"name": "Records", "description": "CRUD operations for financial records with visibility scoping."},
    {"name": "Dashboard", "description": "Fast analytics and reporting aggregation (totals, trends)."},
]

app = FastAPI(
    title="Finance Dashboard Backend",
    description=(
        "A role-based financial record management API. "
        "Supports JWT authentication, RBAC, CRUD records, and dashboard analytics."
    ),
    version="1.0.0",
    contact={"name": "API Support"},
    openapi_tags=tags_metadata,
)

# CORS — allows any frontend origin in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global Exception Handlers ---
# Converts our custom domain exceptions into consistent JSON error responses.
# Every error body has: {"error_code": "...", "detail": "..."}

@app.exception_handler(NotFoundError)
@app.exception_handler(ForbiddenError)
@app.exception_handler(BadRequestError)
@app.exception_handler(UnauthorizedError)
async def custom_http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": type(exc).__name__, "detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


# --- Routers ---
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/", tags=["Health"])
def health_check():
    """Simple liveness check — useful for uptime monitoring."""
    return {"status": "ok", "message": "Finance API is running"}


@app.on_event("startup")
def on_startup():
    if os.environ.get("VERCEL"):
        print("Vercel environment detected. Seeding ephemeral SQLite database.")
        try:
            import seed
            seed.main()
        except Exception as e:
            print(f"Error seeding database: {e}")
