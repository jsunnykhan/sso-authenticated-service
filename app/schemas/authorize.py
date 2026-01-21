from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class AuthorizeParams(BaseModel):
    scope : str
    response_type : str
    client_id : str
    redirect_uri : str
    code_challenge : str
    code_challenge_method : str
    
class AuthorizeUserParams(AuthorizeParams):
    id: Optional[str] = Field(None, description="User ID")
    
class AuthorizeConsentParams(AuthorizeParams) :
    email : str
    hash: str