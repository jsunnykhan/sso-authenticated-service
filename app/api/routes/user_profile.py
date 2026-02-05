from fastapi import APIRouter, Depends, Request
from app.api.routes.dependency_jwt import validate_jwt_token
from app.db.session import get_db
from app.utils.logger import logger

app = APIRouter()


@app.get("")
async def user_profile(user=Depends(validate_jwt_token)):

    return {
        "email": user.email,
        "name": user.name,
    }
