from fastapi import FastAPI
from app.api.v1.routes import token

app = FastAPI(
    title="SSO Identity Service",
    version="0.0.1",
    docs_url="/v1/docs",
)


app.include_router(token.app, prefix="/v1/oauth", tags=["auth"])
