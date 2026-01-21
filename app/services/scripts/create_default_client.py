from fastapi import Depends
from app.db.session import Session, get_db
from app.services.client import create_oauth_client
from app.utils.token import Token
from app.db.models.oauth_client import OAuthClient


def main(db: Session = Depends(get_db)):
    default_client_name = "custos_default_client"
    default_redirect_uris = "https://custos.sunnykhan.pro/api/auth/callback/custos-sso"
    token_util = Token()

    client_id = token_util.get_client_id()
    token_util.create_client_private_key(client_id)
    client_secret = token_util.get_client_secret(client_id)

    new_client = OAuthClient(
        client_name=default_client_name,
        redirect_uris=default_redirect_uris,
        client_id=client_id,
        client_secret=client_secret,
    )

    client = create_oauth_client(
        client=new_client,
        db=db,
    )

    if client:
        print("Default client created successfully.")
    else:
        print("Default client already exists.")


if __name__ == "__main__":
    main()
