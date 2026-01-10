from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.routes import auth, daily_meal, config
from app.tasks.meal_scheduler import start_meal_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_meal_scheduler()
    yield
    print("Shutting down all corns... ")


start_meal_scheduler()

app = FastAPI(
    title="FastAPI Auth Boilerplate",
    version="0.0.1",
    docs_url="/api/v1/docs",
    lifespan=lifespan,
)


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    daily_meal.router, prefix="/api/v1/daily-meals", tags=["daily_meals"]
)
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
