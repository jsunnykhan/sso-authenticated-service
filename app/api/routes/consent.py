from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.session import get_db
from app.schemas.authorize import AuthorizeParams, AuthorizeUserParams
from app.services.client import get_oauth_client_by_id
from app.services.consent import create_user_consent
from app.services.redis import store_auth_code
from app.services.user import get_user_by_id

app = APIRouter()


BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
async def consent(request: Request, params: AuthorizeUserParams = Depends()):
    return templates.TemplateResponse(
        "consent.html",
        {
            "request": request,
            "scope": params.scope,
            "response_type": params.response_type,
            "client_id": params.client_id,
            "user_id": params.id,
            "redirect_uri": params.redirect_uri,
            "code_challenge": params.code_challenge,
            "code_challenge_method": params.code_challenge_method,
        },
    )


@app.post("/approve")
async def perform_consent(
    request: Request,
    user_id: str = Form(...),
    scope: str = Form(...),
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    code_challenge: str = Form(...),
    code_challenge_method: str = Form(...),
    db=Depends(get_db),
):
    client = get_oauth_client_by_id(client_id, db)
    if not client:
        return RedirectResponse(
            url=f"{redirect_uri}?error=invalid_client", status_code=303
        )
    user = get_user_by_id(user_id, db)
    if not user:
        return RedirectResponse(
            url=f"{redirect_uri}?error=invalid_user", status_code=303
        )
    consent = create_user_consent(user_id, client_id, db)
    if not consent:
        return RedirectResponse(
            url=f"{redirect_uri}?error=consent_error", status_code=303
        )

    params = AuthorizeParams(
        scope=scope,
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )
    code = store_auth_code(params)
    if not code:
        return RedirectResponse(
            url=f"{redirect_uri}?error=server_error", status_code=303
        )
    redirect_url = f"{redirect_uri}?code={code}"
    return RedirectResponse(url=redirect_url, status_code=303)