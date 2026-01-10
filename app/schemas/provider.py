from pydantic import BaseModel
from typing import Optional

class ProviderCreate(BaseModel):
    name: str
    client_id: str
    client_secret: str
    redirect_url: Optional[str] = None

class ValidateProvider(BaseModel):
    client_id: str
    client_secret: str

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_url: Optional[str] = None
