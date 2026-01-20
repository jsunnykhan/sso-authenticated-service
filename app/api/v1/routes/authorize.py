

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db


app = APIRouter()

@app.get("/")
async def authorize(client_id: str, redirect_uri: str, state: str, request: Request, db=Depends(get_db)):
    return None