from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

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
            "userinfo_endpoint": f"{base_url}/oauth/userinfo",
            "jwks_uri": f"{base_url}/.well-known/jwks.json",
            "response_types_supported": ["code", "id_token", "token id_token"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "scopes_supported": ["openid", "profile", "email"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
        }
    )


# JWKS endpoint
@app.get("/jwks.json")
async def jwks():
    """
    Return a dummy JWKS for testing (replace with your real keys)
    """
    # Example key, replace with your actual RSA public key in production
    jwk = {
        "keys": [
            {
                "kty": "RSA",
                "kid": "1",
                "use": "sig",
                "alg": "RS256",
                "n": "replace_with_your_modulus",
                "e": "AQAB",
            }
        ]
    }
    return JSONResponse(content=jwk)


@app.get("/{path:path}")
async def catchall_well_known(path: str):
    return JSONResponse(content={})
