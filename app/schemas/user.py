from typing import Optional
from pydantic import BaseModel
from app.schemas.password import PasswordSchema


class UserSchema(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    password: Optional[PasswordSchema] = None

    model_config = {
        "from_attributes": True,
    }
