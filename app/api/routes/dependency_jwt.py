from fastapi import Depends, HTTPException, Header, status

from app.db.session import get_db

from app.services.user import get_user_by_email
from app.utils.token import Token
from app.utils.logger import logger
from app.services.redis import is_token_revoked


async def validate_jwt_token(authorization: str = Header(...), db=Depends(get_db)):

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    access_token = authorization.split(" ")[1]
    token = Token()

    data = token.decode_token(access_token)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if await is_token_revoked(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    email = data.get("email")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid user",
        )
        
    return user
