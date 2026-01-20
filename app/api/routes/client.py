from fastapi import APIRouter, Depends, Form
from app.api.routes.dependency import Validate_API_Keys
from app.db.models.oauth_client import OAuthClient
from app.db.session import get_db
from app.schemas.api_response import APIResponse
from app.schemas.authorize import AuthorizeParams
from app.schemas.client import ClientBase, ClientCreate
from app.services.client import create_oauth_client, get_clients
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
