
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from app.db.models.user_identities import UserIdentity

class IdentityService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def get_identities_by_user(self, user_id: str):
        identities = self.db.query(UserIdentity).filter(UserIdentity.user_id == user_id).all()
        return identities
    
    def get_identity_by_user_and_provider(self, user_id: str, provider_id: str):
        identity = self.db.query(UserIdentity).filter(
            UserIdentity.user_id == user_id,
            UserIdentity.provider_id == provider_id
        ).first()
        return identity
    
    def create_identity_between_user_and_provider(self, user_id: str, provider_id: str, provider_user_id: str):
        identity = UserIdentity(
            user_id=user_id,
            provider_id=provider_id,
            provider_user_id=provider_user_id
        )
        self.db.add(identity)
        self.db.commit()
        self.db.refresh(identity)
        return identity
    
    def get_user_identity(self, user_id: str, provider_id: str):
        identity = self.db.query(UserIdentity).filter(
            UserIdentity.user_id == user_id,
            UserIdentity.provider_id == provider_id
        ).first()
        return identity