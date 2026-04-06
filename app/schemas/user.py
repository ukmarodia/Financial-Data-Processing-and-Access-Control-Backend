from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserRole


class UserResponse(BaseModel):
    """What we return when someone asks for user info. Never includes password."""
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Admin changes a user's role."""
    role: UserRole


class UserStatusUpdate(BaseModel):
    """Admin activates/deactivates a user."""
    is_active: bool
