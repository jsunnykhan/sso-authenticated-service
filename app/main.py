from fastapi import FastAPI
from app.api.routes import authorize, token, consent, login, profile

app = FastAPI(
    title="SSO Identity Service",
    version="0.0.1",
    docs_url="/v1/docs",
)


app.include_router(authorize.app, prefix="/oauth/authorize", tags=["authorize"])
app.include_router(token.app, prefix="/oauth/token", tags=["token"])
app.include_router(profile.app, prefix="/oauth/profile", tags=["profile"])

app.include_router(login.app, prefix="/oauth/login", tags=["login"])
app.include_router(consent.app, prefix="/oauth/consent", tags=["consent"])
