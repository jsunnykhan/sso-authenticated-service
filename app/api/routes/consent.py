from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.session import get_db
from app.schemas.authorize import AuthorizeConsentParams , AuthorizeUserParams
from app.services.client import get_oauth_client_by_id
from app.services.consent import create_user_consent
from app.services.redis import store_auth_code
from app.services.user import create_new_user

app = APIRouter()


BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("")
async def consent(request: Request, params: AuthorizeConsentParams = Depends()):
    return templates.TemplateResponse(
        "consent.html",
        {
            "request": request,
            "scope": params.scope,
            "response_type": params.response_type,
            "client_id": params.client_id,
            "email": params.email,
            "hash" : params.hash,
            "redirect_uri": params.redirect_uri,
            "code_challenge": params.code_challenge,
            "code_challenge_method": params.code_challenge_method,
        },
    )


@app.post("/approve")
async def perform_consent(
    _: Request,
    scope: str = Form(...),
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    code_challenge: str = Form(...),
    code_challenge_method: str = Form(...),
    email :str = Form(...),
    hash : str = Form(...),
    db=Depends(get_db),
):
    client = get_oauth_client_by_id(client_id, db)
    if not client:
        return RedirectResponse(
            url=f"{redirect_uri}?error=invalid_client", status_code=303
        )
    user = create_new_user(email , hash , db)
    if not user:
        return RedirectResponse(
            url=f"{redirect_uri}?error=failed_to_register", status_code=303
        )
    user_id = str(user.id)
    consent = create_user_consent(user_id, client_id, db)
    if not consent:
        return RedirectResponse(
            url=f"{redirect_uri}?error=consent_error", status_code=303
        )

    params = AuthorizeUserParams(
        id=user_id,
        scope=scope,
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )
    code = await store_auth_code(params)
    if code is None:
        return RedirectResponse(
            url=f"{redirect_uri}?error=server_error", status_code=303
        )
    redirect_url = f"{redirect_uri}?code={code}"
    return RedirectResponse(url=redirect_url, status_code=303)
