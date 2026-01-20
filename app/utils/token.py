import base64
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings
from app.schemas.jwt import JWTToken

from pathlib import Path
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from typing import cast
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


class Token:
    def __init__(self):
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_MINUTES
        self.SECRET_KEY = settings.JWT_SECRET_KEY
        self.ALGORITHM = settings.JWT_ALGORITHM
        self.KEYS_DIR = Path("./keys")
        self.KEYS_DIR.mkdir(parents=True, exist_ok=True)

    def get_access_token(self, token_data: JWTToken):
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = token_data.model_dump()
        payload.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_refresh_token(self, token_data: JWTToken):
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = token_data.model_dump()
        payload.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_token(self, token: str):
        return jwt.decode(
            token,
            self.SECRET_KEY,
            algorithms=[self.ALGORITHM],
            options={"verify_aud": False},
        )

    def get_client_id(self):
        return str(uuid.uuid4())

    def get_filepath_for_client_secret(self, client_id: str) -> Path:
        return self.KEYS_DIR / f"{client_id}.pem"

    def create_client_private_key(self, client_id: str):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
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
            raise FileNotFoundError("PEM file not found")

        pem_bytes = pem_path.read_bytes()

        # SHA-256 fingerprint
        digest = hashlib.sha256(pem_bytes).hexdigest()
        return digest

    def verify_client_secret(self, data):
        try:
            filename = self.get_filepath_for_client_secret(data.client_id)
            secret = data.client_secret
            with open(filename, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
            public_key = cast(RSAPublicKey, private_key.public_key())

            public_key.verify(
                secret.encode(),
                b"expected_message",
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            print("Client secret verification failed:", e)
            return False
        return True

    def verify_pkce(self, code_verifier: str, code_challenge: str) -> bool:
        digest = hashlib.sha256(code_verifier.encode()).digest()
        computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return computed == code_challenge
