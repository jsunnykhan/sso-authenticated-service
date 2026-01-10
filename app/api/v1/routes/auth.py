from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, PasswordResetRequest
from app.services.user import (
    create_user,
    authenticate_user,
    get_current_user,
    get_user_permissions,
    reset_user_password,
)
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.token import create_access_token
from ..dependencies import permission_required
from app.schemas.response import ResponseModel

router = APIRouter()


@router.post("/signup", response_model=ResponseModel)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    create_user(user, db)
    return ResponseModel(
        code=status.HTTP_201_CREATED, message="Signup Successfull", data=None
    )


@router.post("/login", response_model=ResponseModel)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(form_data.email, form_data.password, db)
    print(user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token(data={"sub": user.email, "role": user.role})
    return ResponseModel(
        code=status.HTTP_201_CREATED,
        message="Login Successfull",
        data={"access_token": token, "token_type": "bearer"},
    )


@router.get(
    "/me",
    response_model=ResponseModel[UserResponse],
    dependencies=[Depends(permission_required())],
)
def read_users_me(current_user=Depends(get_current_user)):
    return ResponseModel(code=status.HTTP_200_OK, message="Success", data=current_user)


@router.get(
    "/permissions",
    dependencies=[Depends(permission_required())],
    response_model=ResponseModel,
)
def read_permissions(
    current_user=Depends(get_current_user),
):

    return ResponseModel(
        code=status.HTTP_200_OK,
        message="Success",
        data=get_user_permissions(current_user.role),
    )


@router.post(
    "/reset-password",
    dependencies=[Depends(permission_required())],
    response_model=ResponseModel,
)
def reset_pass(
    body: PasswordResetRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reset_user_password(current_user, body.new_password, db)
    return ResponseModel(
        code=status.HTTP_205_RESET_CONTENT,
        message="Password reset successful",
        data=None,
    )
