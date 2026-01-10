from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.config import Config
from functools import lru_cache
from uuid import UUID

from app.schemas.config import ConfigCreate


@lru_cache(maxsize=128)
def get_config_cached() -> dict:
    """Cached config values."""
    from app.db.session import get_db

    db = next(get_db())  # only works if session generator is simple
    return {cfg.key: cfg.value for cfg in db.query(Config).all()}


def refresh_config_cache():
    """Call this after config is updated."""
    get_config_cached.cache_clear()


def get_config_value(key: str) -> str | None:
    return get_config_cached().get(key)


def get_config_list(db: Session):
    return db.query(Config).all()


def create_config(body: ConfigCreate, db: Session):
    config = Config(**body.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    refresh_config_cache()


def update_config(id: UUID, body: ConfigCreate, db: Session):
    config = db.query(Config).filter_by(id=id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found.")
    config.key = body.key
    config.value = body.value
    db.commit()
    db.refresh(config)
    refresh_config_cache()


def delete_config(id: UUID, db: Session):
    config = db.query(Config).filter_by(id=id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found.")
    db.delete(config)
    db.commit()
    refresh_config_cache()
