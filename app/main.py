from fastapi import FastAPI
from app.api.v1.routes import auth

app = FastAPI(
    title="SSO Authenticated Service",
    version="0.0.1",
    docs_url="/api/v1/docs",
)


app.include_router(auth.router, prefix="/api/v1/oauth", tags=["oauth"])
