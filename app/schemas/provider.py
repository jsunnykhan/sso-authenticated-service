from pydantic import BaseModel
from typing import Optional

class ProviderCreate(BaseModel):
    name: str
    client_id: str
    client_secret: str
    redirect_url: Optional[str]

class ValidateProvider(BaseModel):
    client_id: str
    client_secret: str

class ProviderUpdate(BaseModel):
    name: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    redirect_url: Optional[str]
