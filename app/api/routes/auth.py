from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, rate_limit_login
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Creates a new user. Automatically assigns Viewer role."""
    return AuthService.register_user(db, req)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_login)])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login.
    Accepts form data (username/password) from Swagger UI.
    """
    req = LoginRequest(email=form_data.username, password=form_data.password)
    return AuthService.authenticate_user(db, req)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's own profile. Available to all roles."""
    return current_user
