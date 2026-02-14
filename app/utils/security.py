# hash_password, verify_password, create_access_token, create_refresh_token

from datetime import datetime, timedelta,timezone
from fastapi import HTTPException
from app.utils.logger import logger
from jose import jwt
from passlib.context import CryptContext
import secrets  # Refresh token generator

from app.utils.config import settings

pwd_maker = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_maker.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_maker.verify(password, hashed_password)


def create_access_token(data: dict, exprires_minutes: int | None = None):    # userid,email,role
    
    to_encode = data.copy()  # Copy data so original dict won't change
    expire_time = datetime.now(timezone.utc)+ timedelta(minutes=exprires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_time})
    logger.info(f"Access token created for user_id: {data.get('user_id')}, expires at {expire_time}")
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


def decode_access_token(token: str):     # userid,email,role
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except Exception as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    
def create_refresh_token():
    return secrets.token_urlsafe(32)  # Generates secure(URLsafe) random string
