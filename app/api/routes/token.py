import code
from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException, Request

from app.db.session import get_db
from app.schemas.jwt import JWTToken
from app.services.client import get_oauth_client_by_id
from app.services.redis import consume_auth_code
from app.services.user import get_user_by_id
from app.utils.logger import logger
from app.utils.token import Token
from app.core.config import settings

from app.utils.url import normalize_url

app = APIRouter()


@app.post("")
async def exchange_token(
    _: Request,
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str = Form(...),
    db=Depends(get_db),
):
    token = Token()

    if grant_type != "authorization_code":
        return HTTPException(status_code=400, detail="Invalid grant type")

    if not code:
        logger.error("Authorization code is missing")
        return HTTPException(status_code=400, detail="Authorization code is required")

    redis_res = await consume_auth_code(code)
    if not redis_res:
        logger.error(f"Invalid or expired authorization code: {code}")
        return HTTPException(
            status_code=400, detail="Invalid or expired authorization code"
        )

    is_valid_pkce = token.verify_pkce(code_verifier, redis_res.code_challenge)

    if not is_valid_pkce:
        logger.error("Invalid PKCE code verifier")
        return HTTPException(status_code=400, detail="Invalid PKCE code verifier")

    client_id = redis_res.client_id

    client = get_oauth_client_by_id(client_id, db)

    if not client:
        logger.error(f"Client not found: {client_id}")
        return HTTPException(status_code=400, detail="Invalid client")

    redirect_url = normalize_url(redirect_uri)
    redirect_uri_client = normalize_url(client.redirect_uris)
    if (
        redirect_uri_client.netloc != redirect_url.netloc
        and redirect_uri_client.path != redirect_url.path
    ):
        logger.error(
            f"Redirect URI mismatch: expected {client.redirect_uris}, got {redirect_uri} {client.redirect_uris} {redirect_url}"
        )
        return HTTPException(status_code=400, detail="Invalid redirect URI")

    user = get_user_by_id(str(redis_res.id), db)
    if not user:
        logger.error(f"User not found: {redis_res.id}")
        return HTTPException(status_code=400, detail="Invalid user")

    jwt_token = JWTToken(
        email=str(user.email),
        client_id=client_id,
        sub=str(user.email),
        aud=client.client_name,
        iss=settings.IDP_ISSUER,
        exp=int((datetime.utcnow().timestamp()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    access_token = token.get_access_token(jwt_token)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
