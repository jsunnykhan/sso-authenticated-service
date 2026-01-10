from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import cast, Any
from app.constants.roles import ROLE_PERMISSIONS, Role
from app.db.models.user import User
from app.schemas.user import UserCreate
from app.utils.hash import get_password_hash, verify_password
from app.db.session import get_db
from app.utils.token import decode_access_token
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_user(user: UserCreate, db: Session):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw,
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, cast(str, user.hashed_password)):
        return False
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = db.query(User).filter(User.email == email).first()
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_permissions(role: str):
    return ROLE_PERMISSIONS.get(cast(Role, role), [])


def reset_user_password(user: User, new_pass: str, db: Session):
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = cast(Any, get_password_hash(new_pass))
    db.commit()
