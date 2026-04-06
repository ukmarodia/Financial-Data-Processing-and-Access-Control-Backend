from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.exceptions import BadRequestError, UnauthorizedError


class AuthService:
    

    @staticmethod
    def register_user(db: Session, req: RegisterRequest) -> User:
        
        
       
        existing_user = db.query(User).filter(User.email == req.email).first()
        if existing_user:
            raise BadRequestError("Email already registered")

        new_user = User(
            email=req.email,
            full_name=req.full_name,
            hashed_password=hash_password(req.password)
        )
        
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()
            raise BadRequestError("Could not create user due to a database constraint.")

    @staticmethod
    def authenticate_user(db: Session, req: LoginRequest) -> TokenResponse:
       
        user = db.query(User).filter(User.email == req.email).first()
        
        if not user or not verify_password(req.password, user.hashed_password):
           
            raise UnauthorizedError("Incorrect email or password")
            
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")

        
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        return TokenResponse(access_token=access_token)
