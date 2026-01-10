#!/usr/bin/env python3
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from sqlalchemy.orm import Session

KEYS_DIR = Path("./keys")
KEYS_DIR.mkdir(parents=True, exist_ok=True)


def generate_client_id() -> str:
    return str(uuid.uuid4())


def generate_pem(client_id: str) -> Path:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pem_path = KEYS_DIR / f"{client_id}.pem"
    pem_path.write_bytes(pem_bytes)

    return pem_path


def generate_client_secret(pem_path: Path) -> str:
    import hashlib
    return hashlib.sha256(pem_path.read_bytes()).hexdigest()


def main():
    provider_name = "defaultProvider"
    redirect_url = "https://example.com/callback"

    

    try:

        client_id = generate_client_id()
        pem_path = generate_pem( client_id)
        client_secret = generate_client_secret(pem_path)

        provider : dict = { 
                           
            "name":provider_name,
            "client_id":client_id,
            "client_secret": client_secret,
            "redirect_url" : redirect_url,
        }
        print("✅ Provider created")
        print(provider)
    
    except Exception as e:
        print("❌ Error creating provider:", e)

if __name__ == "__main__":
    main()
