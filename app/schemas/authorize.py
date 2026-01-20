from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class AuthorizeParams(BaseModel):
    scope : str
    response_type : str
    client_id : str
    redirect_uri : str
    code_challenge : str
    code_challenge_method : str