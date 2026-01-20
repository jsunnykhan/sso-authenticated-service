from fastapi import Header, HTTPException, status, Depends

from app.db.session import get_db

from app.schemas.client import ClientBase
from app.services.client import get_oauth_client_by_id


async def Validate_API_Keys(
    x_client_id: str = Header(...),
    x_client_secret: str = Header(...),
    db=Depends(get_db),
):
    if(not x_client_id) or (not x_client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client credentials missing",
        )
        
    client = get_oauth_client_by_id(x_client_id, db)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    if client.client_secret != x_client_secret and client.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )
    return client

# later client and secret validation can be more complex with private keys