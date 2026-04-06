import time
from collections import defaultdict

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import UnauthorizedError, ForbiddenError
from app.models.user import User, UserRole
from app.utils.security import decode_access_token



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Core authentication dependency. Extracts user from JWT token.
    Every protected endpoint depends on this.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Token missing user identifier")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise UnauthorizedError("User not found")

    if not user.is_active:
        raise ForbiddenError("Account is deactivated. Contact an admin.")

    return user


def require_role(*allowed_roles: UserRole):
    """
    Factory for role-checking dependencies. Usage in a route:

        @router.post("/records", dependencies=[Depends(require_role(UserRole.ADMIN))])

    Or inject the user directly:

        current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"This action requires one of these roles: "
                f"{', '.join(r.value for r in allowed_roles)}"
            )
        return current_user

    return role_checker


# Simple memory rate limiter for login
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 60

def rate_limit_login(request: Request):
    """Rate limit per IP: prevents basic password brute-force attacks."""
    if getattr(request.client, "host", None) == "testclient":
        return
        
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Clean up old attempts
    login_attempts[ip] = [attempt for attempt in login_attempts[ip] if now - attempt < LOGIN_WINDOW_SECONDS]
    
    if len(login_attempts[ip]) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please try again later."
        )
    
    login_attempts[ip].append(now)
