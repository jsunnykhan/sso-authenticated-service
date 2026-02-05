from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.jwt import JWTToken
from app.core.security import get_idp_private_key, get_idp_public_key, create_access_token
from pathlib import Path
import hashlib
import base64
import uuid

class Token:
    def __init__(self):
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_MINUTES
        self.KEYS_DIR = Path("./keys")
        self.KEYS_DIR.mkdir(parents=True, exist_ok=True)

    def get_access_token(self, token_data: JWTToken):
        return create_access_token(token_data.model_dump())

    def get_refresh_token(self, token_data: JWTToken):
        # Using the same logic for refresh token for now, but keeping it separate for future divergence
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = token_data.model_dump()
        payload.update({"exp": int(expire.timestamp()), "iat": int(datetime.now(timezone.utc).timestamp()), "type": "refresh"})
        return jwt.encode(payload, get_idp_private_key(), algorithm="RS256")

    def decode_token(self, token: str):
        try:
            return jwt.decode(
                token,
                get_idp_public_key(),
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        except JWTError:
            return None

    def get_client_id(self):
        return str(uuid.uuid4())

    def get_filepath_for_client_secret(self, client_id: str) -> Path:
        return self.KEYS_DIR / f"{client_id}.pem"

    def create_client_private_key(self, client_id: str):
        # This seems to be for client authentication, keeping it as is for compatibility
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pem_file = self.get_filepath_for_client_secret(client_id)
        with open(pem_file, "wb") as f:
            f.write(pem_bytes)
        return True

    def get_client_secret(self, client_id: str) -> str:
        filename = self.get_filepath_for_client_secret(client_id)
        pem_path = Path(filename)
        if not pem_path.exists():
            # If not exists, maybe it was stored as a string in DB? 
            # The original code raised FileNotFoundError.
            raise FileNotFoundError(f"PEM file not found for client {client_id}")
        pem_bytes = pem_path.read_bytes()
        return hashlib.sha256(pem_bytes).hexdigest()

    def verify_pkce(self, code_verifier: str, code_challenge: str) -> bool:
        if not code_verifier or not code_challenge:
            return False
        digest = hashlib.sha256(code_verifier.encode()).digest()
        computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return computed == code_challenge
