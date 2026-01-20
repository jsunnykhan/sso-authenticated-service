from typing import cast
from sqlalchemy.orm import Session
from app.db.models.password import Password
from app.db.models.user import User
from app.schemas.user import UserSchema
from app.utils.hash import verify_password_hash, get_password_hash


def get_user_username_and_password(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password_hash(password, user.password.password):
        return None

    return user


def get_user_by_id(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    return user


def create_new_user(email: str, password: str, db: Session):
    hash_password = get_password_hash(password)

    user = User(email=email, name=None)
    user.password = Password(algorithm="", salt="", password=hash_password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
