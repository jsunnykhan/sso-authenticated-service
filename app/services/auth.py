

from typing import cast
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.utils.hash import verify_password , get_password_hash


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def user_exists(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, cast(str, user.hashed_password)):
            return False
        return user
    
    def create_user(self, email: str, password: str):
        hashed_pw = get_password_hash(password)
        
        new_user = User(
            email=email,
            hashed_password=hashed_pw,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
