from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status

from app.db.session import get_db
from app.schemas.jwt import JWTToken
from app.services.client import get_oauth_client_by_id
from app.services.redis import consume_auth_code, store_access_token
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
    code: str = Form(None),
    redirect_uri: str = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(None),
    refresh_token: str = Form(None),
    code_verifier: str = Form(None),
    db=Depends(get_db),
):
    token_util = Token()

    # Verify Client
    client = get_oauth_client_by_id(client_id, db)
    if not client:
        logger.error(f"Client not found: {client_id}")
        raise HTTPException(status_code=400, detail="Invalid client")

    # Client Secret Verification (Mandatory if secret is set in DB)
    if client.client_secret:
        if not client_secret or client_secret != client.client_secret:
            logger.error(f"Client secret mismatch for client: {client_id}")
            raise HTTPException(status_code=401, detail="Invalid client secret")

    if grant_type == "authorization_code":
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")

        redis_res = await consume_auth_code(code)
        if not redis_res:
            logger.error(f"Invalid or expired authorization code: {code}")
            raise HTTPException(
                status_code=400, detail="Invalid or expired authorization code"
            )

        # PKCE Verification
        if code_verifier:
            is_valid_pkce = token_util.verify_pkce(code_verifier, redis_res.code_challenge)
            if not is_valid_pkce:
                logger.error("Invalid PKCE code verifier")
                raise HTTPException(status_code=400, detail="Invalid PKCE code verifier")
        elif redis_res.code_challenge:
            logger.error("PKCE code verifier missing but challenge was provided")
            raise HTTPException(status_code=400, detail="PKCE code verifier is required")

        # Redirect URI Validation
        if not redirect_uri:
            raise HTTPException(status_code=400, detail="Redirect URI is required for authorization_code grant")
            
        input_redirect = normalize_url(redirect_uri)
        stored_redirect = normalize_url(client.redirect_uris)
        
        if (
            input_redirect.netloc != stored_redirect.netloc or 
            input_redirect.path != stored_redirect.path
        ):
            logger.error(
                f"Redirect URI mismatch: expected {client.redirect_uris}, got {redirect_uri}"
            )
            raise HTTPException(status_code=400, detail="Invalid redirect URI")

        user = get_user_by_id(str(redis_res.id), db)
        if not user:
            logger.error(f"User not found: {redis_res.id}")
            raise HTTPException(status_code=400, detail="Invalid user")
        
        scopes = redis_res.scope.split() if redis_res.scope else ["openid"]

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")
        
        payload = token_util.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid or expired refresh token")
        
        if payload.get("client_id") != client_id:
             raise HTTPException(status_code=400, detail="Refresh token was not issued to this client")

        user = get_user_by_id(payload.get("sub"), db) # Sub is user ID
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        scopes = payload.get("scope", ["openid"])

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported grant type: {grant_type}")

    # Generate Tokens
    jwt_data = JWTToken(
        email=str(user.email),
        client_id=client_id,
        sub=str(user.id),
        aud=client_id,
        iss=settings.IDP_ISSUER,
        scope=scopes,
    )

    access_token = token_util.get_access_token(jwt_data)
    new_refresh_token = token_util.get_refresh_token(jwt_data)
    
    # Store in Redis for revocation support
    await store_access_token(access_token, str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    response = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": new_refresh_token,
        "scope": " ".join(scopes)
    }

    if "openid" in scopes:
        # Generate ID Token
        id_token_payload = jwt_data.model_dump()
        id_token_payload.update({
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc).timestamp()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        })
        # Add profile info if scopes allow
        if "profile" in scopes:
            id_token_payload["name"] = user.name
        if "email" in scopes:
            id_token_payload["email"] = user.email
            id_token_payload["email_verified"] = True
            
        from app.core.security import get_idp_private_key
        from jose import jwt as jose_jwt
        id_token = jose_jwt.encode(id_token_payload, get_idp_private_key(), algorithm="RS256")
        response["id_token"] = id_token

    return response
