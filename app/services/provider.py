
from typing import cast
from fastapi import Depends
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.db.models.provider import Provider
from app.schemas.provider import ValidateProvider , ProviderCreate ,ProviderUpdate

class ProviderService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def get_provider_count(self) -> int:
        count = self.db.query(Provider).count()
        return count
        
    def validate_client(self, data : ValidateProvider) -> bool | Provider:
        provider = self.db.query(Provider).filter(
            Provider.client_id == data.client_id,
            Provider.client_secret == data.client_secret,
        ).first()
        
        if not provider:
            return False
        return provider
     
    def get_provider_by_client_id(self, client_id: str):
        provider = self.db.query(Provider).filter(Provider.client_id == client_id).first()
        return provider
    
    def related_identities(self, provider_id: str):
        provider = self.db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            return None
        return provider.identities
    
    def create_provider(self, data : ProviderCreate):
        provider = Provider(
            name=data.name,
            client_id=data.client_id,
            client_secret=data.client_secret,
            redirect_uris=data.redirect_url,
        )
        self.db.add(provider)
        self.db.commit()
        self.db.refresh(provider)
        return provider
    
    def get_provider(self, provider_id: str):
        provider = self.db.query(Provider).filter(Provider.id == provider_id).first()
        return provider
    
    def list_providers(self):
        providers = self.db.query(Provider).all()
        return providers
    
    def delete_provider(self, provider_id: str):
        provider = self.db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            return False
        self.db.delete(provider)
        self.db.commit()
        return True
    
    def update_provider(self, data: ProviderUpdate, provider_id: str):
        provider: Provider = self.db.query(Provider).filter(Provider.id == provider_id).first()
        if not provider:
            return None
        if data.name:
            provider.name = data.name # type: ignore
        if data.client_id:
            provider.client_id = data.client_id # type: ignore
        if data.client_secret:
            provider.client_secret = data.client_secret # type: ignore
        if data.redirect_url:
            provider.redirect_url = data.redirect_url # type: ignore
        
        self.db.commit()
        self.db.refresh(provider)
        return provider