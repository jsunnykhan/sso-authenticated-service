from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.dependencies import permission_required
from app.db.session import get_db
from app.schemas.config import ConfigResponse, ConfigCreate
from app.db.models.config import Config
from app.schemas.roles import Role
from app.services.config import (
    create_config,
    get_config_list,
    update_config,
    delete_config,
)
from app.schemas.response import ResponseModel

router = APIRouter(dependencies=[Depends(permission_required(Role.ADMIN))])


@router.post(
    "/",
    response_model=ResponseModel[ConfigResponse],
)
def create(config_in: ConfigCreate, db: Session = Depends(get_db)):
    create_config(config_in, db)
    return ResponseModel(
        code=201,
        message="Config created",
    )


@router.get("/", response_model=ResponseModel[list[ConfigResponse]])
def list_configs(db: Session = Depends(get_db)):
    configs = get_config_list(db)
    return ResponseModel(code=200, message="Success", data=configs)


@router.put("/{config_id}", response_model=ResponseModel[ConfigResponse])
def update(config_id: UUID, body: ConfigCreate, db: Session = Depends(get_db)):
    update_config(id=config_id, body=body, db=db)
    return ResponseModel(code=200, message="Config updated")


@router.delete("/{config_id}", response_model=ResponseModel[None])
def delete(config_id: UUID, db: Session = Depends(get_db)):
    delete_config(id=config_id, db=db)
    return ResponseModel(code=204, message="Config deleted")
