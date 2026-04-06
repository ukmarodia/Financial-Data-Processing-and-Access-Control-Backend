from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserRole, User
from app.schemas.user import UserResponse, UserRoleUpdate, UserStatusUpdate
from app.services.user_service import UserService
from app.api.deps import require_role



router = APIRouter(
    prefix="/users", 
    tags=["Users"],
    dependencies=[Depends(require_role(UserRole.ADMIN))]
)


@router.get("", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    return UserService.get_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
   
    return UserService.get_user_by_id(db, user_id)


@router.patch("/{user_id}/role", response_model=UserResponse)
def change_role(user_id: int, req: UserRoleUpdate, db: Session = Depends(get_db)):
   
    return UserService.change_role(db, user_id, req.role)


@router.patch("/{user_id}/status", response_model=UserResponse)
def change_status(
    user_id: int, 
    req: UserStatusUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    
    return UserService.change_status(db, user_id, req.is_active, self_id=current_user.id)
