from pydantic import BaseModel


class PasswordSchema(BaseModel):
    id: str
    user_id: str
    password: str
    algorithm: str
    salt: str

    model_config = {
        "from_attributes": True,
    }
