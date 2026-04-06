from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.exceptions import NotFoundError, BadRequestError


class UserService:
   

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).order_by(User.id).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        return user

    @staticmethod
    def change_role(db: Session, user_id: int, new_role: UserRole) -> User:
        user = UserService.get_user_by_id(db, user_id)
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_status(db: Session, user_id: int, is_active: bool, self_id: int) -> User:
        if user_id == self_id and not is_active:
            raise BadRequestError("You cannot deactivate your own account")
            
        user = UserService.get_user_by_id(db, user_id)
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user
