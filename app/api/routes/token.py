from fastapi import APIRouter, Depends, Form, Request

from app.db.session import get_db

app = APIRouter()


@app.get("/")
async def authorize(client_id: str, redirect_uri: str, state: str, request: Request, db=Depends(get_db)):
    return None