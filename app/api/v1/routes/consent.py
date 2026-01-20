


from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session  


app = APIRouter()
@app.get("/")
async def consent(client_id: str, redirect_uri: str, state: str, request: Request, ):
    return None

