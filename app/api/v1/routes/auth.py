import base64
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import  AuthResponse , Auth
from app.services.auth import AuthService
from app.schemas.response import ResponseModel
from app.schemas.token import JWTToken
from app.api.v1.dependencies import get_client
from app.services.provider import ProviderService
from app.services.identity import IdentityService
from app.utils.token import Token
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.session import get_db

app = APIRouter()
token_util = Token()

def to_base64url(n):
    # Convert integer to base64url string as per OIDC spec
    b = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
    return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

@app.get("/.well-known/openid-configuration")
async def oidc_discovery():
    return {
        "issuer": settings.settings.IDP_ISSUER,
        "authorization_endpoint": f"{settings.IDP_ISSUER}/authorize",
        "token_endpoint": f"{settings.IDP_ISSUER}/token",
        "userinfo_endpoint": f"{settings.IDP_ISSUER}/userinfo",
        "jwks_uri": f"{settings.IDP_ISSUER}/.well-known/jwks.json",
        "response_types_supported": ["code"]
    }

@app.get("/.well-known/jwks.json")
async def jwks():
    return {
        "keys": [{
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": "main-key-id", # Unique ID for this key
            # "n": to_base64url(public_numbers.n),
            # "e": to_base64url(public_numbers.e),
        }]
    }

@app.post("/authorize", response_model=ResponseModel[AuthResponse])
async def authorize(
    form_data: Auth,
    db: Session = Depends(get_db)
):
   