from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.responses import RedirectResponse
from app.utils.url import normalize_url
from app.services.client import get_oauth_client_by_id
from app.services.redis import revoke_access_token
from app.db.session import get_db

app = APIRouter()

@app.get("")
async def logout(
    request: Request,
    id_token_hint: str = None,
    post_logout_redirect_uri: str = None,
    state: str = None,
    authorization: str = Header(None),
    db=Depends(get_db)
):
    """
    OIDC RP-Initiated Logout.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        await revoke_access_token(token)
    
    # In a real app, clear session cookies here
    
    if post_logout_redirect_uri:
        # Optionally validate post_logout_redirect_uri against client config
        # For simplicity, we just redirect if provided
        url = post_logout_redirect_uri
        if state:
            url += f"&state={state}" if "?" in url else f"?state={state}"
        return RedirectResponse(url=url)
    
    return {"message": "Logged out successfully"}
