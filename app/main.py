from fastapi import FastAPI

from app.routes.auth_me import router as auth_me_router
from app.routes.auth_routes import router as auth_router
from app.routes.health_routes import router as health_router
from app.routes.user_routes import router as user_router
from app.utils.config import settings
from app.utils.logger import logger

app = FastAPI()


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(auth_me_router)

app.include_router(user_router)

@app.get("/")
def root():
    logger.info(f"{settings.APP_NAME} is running in {settings.ENV} environment!!")
    return {"msg": "API is running"}          