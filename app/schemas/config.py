from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ConfigResponse(BaseModel):
    id: UUID
    key: str
    value: str
    model_config = ConfigDict(from_attributes=True)


class ConfigCreate(BaseModel):
    key: str
    value: str

