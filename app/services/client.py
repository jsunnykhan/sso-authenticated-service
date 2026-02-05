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
    client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    return client is not None


def update_oauth_client(client_id: str, client_data: dict, db: Session):
    db_client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    if not db_client:
        return None
    for key, value in client_data.items():
        if value is not None:
            setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_oauth_client(client_id: str, db: Session):
    db_client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    if not db_client:
        return False
    db.delete(db_client)
    db.commit()
    return True


def rotate_client_secret(client_id: str, new_secret: str, db: Session):
    db_client = db.query(OAuthClient).filter(OAuthClient.client_id == client_id).first()
    if not db_client:
        return None
    db_client.client_secret = new_secret
    db.commit()
    db.refresh(db_client)
    return db_client
