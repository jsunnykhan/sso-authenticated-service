from fastapi import Header, HTTPException,Depends
from app.services.provider import ProviderService
from app.schemas.provider import ValidateProvider
from sqlalchemy.orm import Session
from app.db.session import get_db


def get_client(
    client_id: str = Header(..., alias="X-Client-Id"),
    client_secret: str = Header(..., alias="X-Client-Secret"),
    db :Session = Depends(get_db)
):
    provider_service = ProviderService(db)
    data = ValidateProvider(
        client_id=client_id,
        client_secret=client_secret
    )
    provider  = provider_service.validate_client(data)
    if not provider:
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    return provider
