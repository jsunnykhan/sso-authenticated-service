from fastapi import APIRouter, Depends, HTTPException, Request, params, status
from fastapi.responses import RedirectResponse
from app.db.session import get_db
from app.schemas.authorize import AuthorizeParams
from urllib.parse import urlencode, urlparse

from app.services.client import get_oauth_client_by_id
from app.utils.url import normalize_url

app = APIRouter()


@app.get("")
async def authorize(params: AuthorizeParams = Depends(), db=Depends(get_db)):
    client = get_oauth_client_by_id(params.client_id, db)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client_id"
        )
    
    # Redirect URI Validation
    input_redirect = normalize_url(params.redirect_uri)
    stored_redirect = normalize_url(client.redirect_uris)
    
    if (
        input_redirect.netloc != stored_redirect.netloc or 
        input_redirect.path != stored_redirect.path
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid redirect_uri"
        )
        
    return RedirectResponse(
        url=f"/oauth/login?{urlencode(params.dict(exclude_none=True))}"
    )
