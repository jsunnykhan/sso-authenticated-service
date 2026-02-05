from typing import cast
from sqlalchemy.orm import Session
from app.db.models.password import Password
from app.db.models.user import User
from app.core.security import verify_password

def get_user_username_and_password(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.password.password):
        return None

    return user


def get_user_by_id(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    return user


def create_new_user(email: str, password: str, db: Session):

    user = User(email=email, name=None)
    user.password = Password(algorithm="", salt="", password=password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
