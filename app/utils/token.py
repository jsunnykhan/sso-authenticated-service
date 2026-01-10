from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.schemas.token import JWTToken

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"


def get_token(token_data: JWTToken,   expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    expire = datetime.utcnow() + expires_delta
    payload = token_data.dict()
    payload.update({"exp": int(expire.timestamp()) })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])