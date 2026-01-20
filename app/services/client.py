from sqlalchemy.orm import Session

from app.db.models.oauth_client import OAuthClient 


def get_oauth_client_by_id(client_id: str, db: Session):
    return db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()


def is_valid_client(client_id: str, db: Session):
    client = get_oauth_client_by_id(client_id, db)
    if not client:
        return False
    return True
