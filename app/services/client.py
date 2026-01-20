from sqlalchemy.orm import Session

from app.db.models.oauth_client import OAuthClient
from app.schemas import client
from app.schemas.client import ClientBase


def get_clients(db: Session):
    clients = db.query(OAuthClient).all()  # latter get sepecific clients by user_id
    return [
        ClientBase.model_validate(client, from_attributes=True) for client in clients
    ]


def create_oauth_client(client: OAuthClient, db: Session):
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_oauth_client_by_id(client_id: str, db: Session):
    client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    return ClientBase.model_validate(client, from_attributes=True) if client else None


def is_valid_client(client_id: str, db: Session):
    client = get_oauth_client_by_id(client_id, db)
    if not client:
        return False
    return True
