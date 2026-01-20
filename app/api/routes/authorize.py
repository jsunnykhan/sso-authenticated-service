from fastapi import APIRouter, Depends, HTTPException, Request, params, status
from fastapi.responses import RedirectResponse
from app.db.session import get_db
from app.schemas.authorize import AuthorizeParams

from app.services.client import is_valid_client
from app.utils.logger import logger

app = APIRouter()

@app.get("/")
async def authorize(params : AuthorizeParams = Depends(), db=Depends(get_db)):
    logger.info("Authorize endpoint called")
    logger.info(f"Authorize endpoint called with params: {params}")
    if not is_valid_client(params.client_id, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id"
        )

    # logger.info(f"Authorization request received for client_id: {params.client_id}")
    
    return RedirectResponse(
        url=f"/oauth/login?client_id={params.client_id}&response_type={params.response_type}&redirect_uri={params.redirect_uri}"
    )
