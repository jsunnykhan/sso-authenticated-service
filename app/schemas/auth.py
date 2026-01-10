from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Auth(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name = Optional[str]


class AuthResponse(Auth):
    email: str
    access_token: str
    token_type: str = "bearer"  
    refresh_token: str
    exp : int

    class Config:
        orm_mode = True
