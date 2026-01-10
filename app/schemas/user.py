from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from uuid import UUID

from app.schemas.roles import Role


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: constr(min_length=8)
    role: Role


class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


from pydantic import BaseModel, constr


class PasswordResetRequest(BaseModel):
    new_password: constr(min_length=8)


class UserResponse(UserBase):
    id: UUID
    username: str
    email: str
    role: str
    name: Optional[str] = None

    class Config:
        orm_mode = True
