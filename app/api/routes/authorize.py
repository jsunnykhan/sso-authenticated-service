from fastapi import APIRouter, Depends, HTTPException, Request, params, status
from fastapi.responses import RedirectResponse
from app.db.session import get_db
from app.schemas.authorize import AuthorizeParams
from urllib.parse import urlencode

from app.services.client import is_valid_client
from app.utils.logger import logger
from app.core.radis import redis_client

app = APIRouter()


@app.get("/")
async def authorize(params: AuthorizeParams = Depends(), db=Depends(get_db)):
    if not is_valid_client(params.client_id, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client_id"
        )
        
    return RedirectResponse(
        url=f"/oauth/login?{urlencode(params.dict(exclude_none=True))}"
    )
