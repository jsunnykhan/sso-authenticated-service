from fastapi import APIRouter, Depends, Form
from app.api.routes.dependency import Validate_API_Keys
from app.db.models.oauth_client import OAuthClient
from app.db.session import get_db
from app.schemas.api_response import APIResponse
from app.schemas.authorize import AuthorizeParams
from app.schemas.client import ClientBase, ClientCreate, ClientUpdate
from app.services.client import (
    create_oauth_client,
    delete_oauth_client,
    get_clients,
    rotate_client_secret,
    update_oauth_client,
)
import uuid
from app.utils.token import Token

from app.utils.logger import logger

app = APIRouter()


@app.get("", response_model=APIResponse[list[ClientBase]])
def get_client(db=Depends(get_db)):

    clients = get_clients(db)
    return APIResponse(
        success=True,
        message="Clients retrieved successfully",
        data=clients,
    )


@app.post(
    "",
    response_model=APIResponse[ClientBase],
)
async def create_client(
    client: ClientCreate, db=Depends(get_db), auth=Depends(Validate_API_Keys)
):
    token_util = Token()

    client_id = token_util.get_client_id()
    token_util.create_client_private_key(client_id)
    client_secret = token_util.get_client_secret(client_id)

    new_client = OAuthClient(
        client_name=client.client_name,
        redirect_uris=client.redirect_uris,
        client_id=client_id,
        client_secret=client_secret,
    )
    client = create_oauth_client(
        client=new_client,
        db=db,
    )

    return APIResponse(
        success=True,
        message="Client created successfully",
        data=ClientBase.model_validate(client),
    )


@app.put("/{client_id}", response_model=APIResponse[ClientBase])
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db=Depends(get_db),
    auth=Depends(Validate_API_Keys),
):
    updated_client = update_oauth_client(client_id, client_data.dict(exclude_none=True), db)
    if not updated_client:
        return APIResponse(success=False, message="Client not found", status_code=404)
    return APIResponse(
        success=True,
        message="Client updated successfully",
        data=ClientBase.model_validate(updated_client),
    )


@app.delete("/{client_id}", response_model=APIResponse[bool])
async def delete_client(
    client_id: str, db=Depends(get_db), auth=Depends(Validate_API_Keys)
):
    success = delete_oauth_client(client_id, db)
    if not success:
        return APIResponse(success=False, message="Client not found", status_code=404)
    return APIResponse(
        success=True,
        message="Client deleted successfully",
        data=True,
    )


@app.post("/{client_id}/rotate-secret", response_model=APIResponse[ClientBase])
async def rotate_secret(
    client_id: str, db=Depends(get_db), auth=Depends(Validate_API_Keys)
):
    token_util = Token()
    new_secret = token_util.get_client_secret(client_id)  # This generates a new one if file is missing, or uses existing?
    # Wait, the Token.get_client_secret currently reads from file.
    # If I want to ROTATE, I should probably generate a new key file.
    
    token_util.create_client_private_key(client_id)
    new_secret = token_util.get_client_secret(client_id)
    
    updated_client = rotate_client_secret(client_id, new_secret, db)
    if not updated_client:
        return APIResponse(success=False, message="Client not found", status_code=404)
    return APIResponse(
        success=True,
        message="Client secret rotated successfully",
        data=ClientBase.model_validate(updated_client),
    )
