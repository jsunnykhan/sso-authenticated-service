from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

app = APIRouter()


BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
async def consent(
    request: Request,
):
    return templates.TemplateResponse("consent.html", {"request": request})


@app.post("/approve")
async def perform_consent(
    request: Request,
):
    return RedirectResponse(url="/oauth/login?code=consentcode123", status_code=303)
