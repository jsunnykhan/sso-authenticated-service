from pydantic import BaseModel 
from typing import Optional
from typing import List
from datetime import datetime



class JWTToken(BaseModel):
    email: str # User's email address
    client_id: str # The client/application ID
    scope: List[str] = ["read"] # Permissions or scopes associated with the token
    iss: str = "https://sso.example.com" # Issuer of the token
    sub: str # Who or what the token is about
    aud: str # Who the token is intended for
    iat: int = int(datetime.utcnow().timestamp()) # Issued at time
    exp: Optional[int] =None # Expiration time