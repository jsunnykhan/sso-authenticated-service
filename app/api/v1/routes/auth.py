from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import  AuthResponse , Auth
from app.services.auth import AuthService
from app.schemas.response import ResponseModel
from app.schemas.token import JWTToken
from app.api.v1.dependencies import get_client
from app.services.provider import ProviderService
from app.services.identity import IdentityService
from app.utils.token import Token
from app.core.config import settings

router = APIRouter()
auth_service = AuthService()
provider_service = ProviderService()
identity_service = IdentityService()
token_util = Token()

@router.post("/authorize", response_model=ResponseModel[AuthResponse])
def authorize(
    form_data: Auth,
    provider=Depends(get_client)
):
    user = auth_service.user_exists(form_data.email, form_data.password)
    
    if user : 
        identities = identity_service.get_identity_by_user_and_provider(
            user_id=str(user.id),
            provider_id=str(provider.id)
        )
        if not identities:
            identity_service.create_identity_between_user_and_provider(
                user_id=str(user.id),
                provider_id=str(provider.id),
                provider_user_id=str(user.id)
            )   
        

    if not user:
        user = auth_service.create_user(form_data.email, form_data.password)
        
        if not user:
            raise HTTPException(status_code=400, detail="User creation failed")
        
        linked_identity = identity_service.create_identity_between_user_and_provider(
            user_id=str(user.id),
            provider_id=str(provider.id),
            provider_user_id=str(user.id)
        )
        
        if not linked_identity:
            raise HTTPException(status_code=400, detail="Failed to link user with provider")
        
    
    
    token_data = JWTToken(
        email= str(user.email),
        client_id=provider.client_id,
        sub=str(user.id),
        aud=provider.client_id,
    )

    access_token = token_util.get_access_token(token_data)
    refresh_token = token_util.get_refresh_token(token_data)

    return ResponseModel(
        code=status.HTTP_201_CREATED,
        message="Login Successful",
        data={
            "access_token": access_token, 
            "token_type": "bearer", 
            "email": user.email ,
            "refresh_token": refresh_token , 
            "exp" : settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60* 1000
            }
    )
