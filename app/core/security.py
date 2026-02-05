from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt has a 72-character limit
    return pwd_context.hash(password.encode("utf-8")[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain.encode("utf-8")[:72], hashed)

def get_idp_private_key() -> str:
    if not os.path.exists(settings.IDP_PRIVATE_KEY_PATH):
        os.makedirs(os.path.dirname(settings.IDP_PRIVATE_KEY_PATH), exist_ok=True)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(settings.IDP_PRIVATE_KEY_PATH, "wb") as f:
            f.write(pem)
            
        public_key = private_key.public_key()
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(settings.IDP_PUBLIC_KEY_PATH, "wb") as f:
            f.write(pub_pem)
            
    with open(settings.IDP_PRIVATE_KEY_PATH, "r") as f:
        return f.read()

def get_idp_public_key() -> str:
    if not os.path.exists(settings.IDP_PUBLIC_KEY_PATH):
        get_idp_private_key() # This will generate both
    with open(settings.IDP_PUBLIC_KEY_PATH, "r") as f:
        return f.read()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(datetime.now(timezone.utc).timestamp())})
    private_key = get_idp_private_key()
    return jwt.encode(to_encode, private_key, algorithm="RS256")
