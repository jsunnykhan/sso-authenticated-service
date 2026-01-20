from pydantic import BaseModel


class ClientBase(BaseModel):
    client_id: str
    client_secret: str
    redirect_uris: str
    client_name: str
    
    
    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    redirect_uris: str
    client_name: str
