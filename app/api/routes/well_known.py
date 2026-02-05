from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.core.security import get_idp_public_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

app = APIRouter()

# OpenID Connect Discovery
@app.get("/openid-configuration")
async def openid_configuration(request: Request):
    """
    Returns the OIDC discovery document.
    """
    base_url = str(request.base_url).rstrip("/")
    return JSONResponse(
        content={
            "issuer": base_url,
            "authorization_endpoint": f"{base_url}/oauth/authorize",
            "token_endpoint": f"{base_url}/oauth/token",
            "userinfo_endpoint": f"{base_url}/oauth/user_info",
            "jwks_uri": f"{base_url}/.well-known/jwks.json",
            "logout_endpoint": f"{base_url}/oauth/logout",
            "response_types_supported": ["code", "token", "id_token", "code token", "code id_token", "token id_token", "code token id_token"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "scopes_supported": ["openid", "profile", "email", "offline_access"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
            "grant_types_supported": ["authorization_code", "refresh_token", "client_credentials"],
            "claims_supported": ["sub", "iss", "auth_time", "name", "given_name", "family_name", "nickname", "profile", "picture", "website", "email", "email_verified", "locale", "zoneinfo"],
            "claims_parameter_supported": False,
            "request_parameter_supported": True,
            "request_uri_parameter_supported": True,
            "require_request_uri_registration": False,
        }
    )

def int_to_base64(value: int) -> str:
    """Converts an integer to a base64url-encoded string."""
    value_hex = hex(value)[2:]
    if len(value_hex) % 2 == 1:
        value_hex = '0' + value_hex
    value_bytes = bytes.fromhex(value_hex)
    return base64.urlsafe_b64encode(value_bytes).rstrip(b'=').decode('utf-8')

# JWKS endpoint
@app.get("/jwks.json")
async def jwks():
    """
    Return the real JWKS for the IdP.
    """
    public_key_pem = get_idp_public_key()
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    
    if not isinstance(public_key, rsa.RSAPublicKey):
        return JSONResponse(status_code=500, content={"error": "Invalid public key type"})

    numbers = public_key.public_numbers()
    
    jwk = {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "kid": "main-idp-key",
                "alg": "RS256",
                "n": int_to_base64(numbers.n),
                "e": int_to_base64(numbers.e),
            }
        ]
    }
    return JSONResponse(content=jwk)

@app.get("/{path:path}")
async def catchall_well_known(path: str):
    return JSONResponse(content={})
