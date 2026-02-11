from urllib.parse import urlencode
from app.services.redis import store_auth_code
from app.services.user import (
    create_new_user,
    get_user_by_email,
    get_user_username_and_password,
)
from app.utils.logger import logger
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.session import get_db
from pathlib import Path
from app.core.security import hash_password as get_password_hash

from app.schemas.authorize import (
    AuthorizeParams,
    AuthorizeUserParams,
    AuthorizeConsentParams,
)

app = APIRouter()


BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("", response_class=HTMLResponse)
async def login(request: Request, params: AuthorizeParams = Depends()):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "scope": params.scope,
            "response_type": params.response_type,
            "client_id": params.client_id,
            "redirect_uri": params.redirect_uri,
            "code_challenge": params.code_challenge,
            "code_challenge_method": params.code_challenge_method,
            "state": params.state,
        },
    )


@app.post("")
async def perform_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    scope: str = Form(...),
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    code_challenge: str = Form(...),
    code_challenge_method: str = Form(...),
    state: str = Form(...),
    db=Depends(get_db),
):
    params = AuthorizeUserParams(
        id="",
        scope=scope,
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        state=state,
    )
    user = get_user_by_email(email, db)

    if user is None:
        hash_pass = get_password_hash(password)
        consent_params = AuthorizeConsentParams(
            **params.model_dump(), email=email, hash=hash_pass
        )
        return RedirectResponse(
            url=f"/oauth/consent?{urlencode(consent_params.model_dump())}",
            status_code=303,
        )

    is_valid_pass = get_user_username_and_password(email, password, db)
    if not is_valid_pass:
        return RedirectResponse(
            url=f"{redirect_uri}?error=access_denied", status_code=302
        )

    user_params = params.model_copy(update={"id": str(user.id)})
    code = await store_auth_code(data=user_params)
    redirect_url = f"{redirect_uri}?code={code}&state={state}"
    return RedirectResponse(url=redirect_url, status_code=302)
