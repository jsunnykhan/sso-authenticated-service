from typing import cast
from sqlalchemy.orm import Session
from app.db.models.password import Password
from app.db.models.user import User
from app.utils.hash import verify_password_hash, get_password_hash


def get_user_username_and_password(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password_hash(password, cast(str, user.hashed_password)):
        return False
    return user


def create_new_user(email: str, password: str, db: Session):
    hash_password = get_password_hash(password)

    user = User(email, password=Password(algorithm="", salt="", password=hash_password))

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
