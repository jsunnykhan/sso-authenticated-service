from fastapi import APIRouter, Depends, Request
from app.api.routes.dependency_jwt import validate_jwt_token
from app.db.session import get_db
from app.utils.logger import logger

app = APIRouter()


@app.get("")
async def user_info(user=Depends(validate_jwt_token)):
    """
    OIDC UserInfo endpoint.
    """
    return {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "email_verified": True,
    }
