from app.db.models.user import User
from sqlalchemy.orm import Session

from app.db.models.user_consent import UserConsent


def get_consent(user_id: str, client_id: str, db: Session):
    user = db.query(UserConsent).filter(UserConsent.user_id == user_id and UserConsent.client_id == client_id).first()
    return user

def create_user_consent(user_id: str, client_id: str, db: Session):
    consent = UserConsent(user_id=user_id, client_id=client_id)
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent