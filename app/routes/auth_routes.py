from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import  HTTPBearer
from app.database.cursor_config import get_db
from app.middleware.auth_me import get_current_user
from app.schemas.auth_schema import SignupRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from app.utils.response_handler import api_response
from app.services.auth_service import auth_signup, auth_login, auth_refresh, auth_logout, delete_user
from app.utils.logger import logger

router = APIRouter(tags=["Authentication"])

bearer_scheme = HTTPBearer()

@router.post("/signup")
def signup(payload: SignupRequest, db=Depends(get_db)):
    try:
        logger.info(f"Signup attempt for email: {payload.email} at /signup endpoint")
        cursor, conn = db

        data = auth_signup(cursor, conn, payload)
        return api_response(201, "Signup successful", data=data)
    except Exception as e:
        logger.error(f"Signup failed for email: {payload.email} with error: {str(e)}")
        raise HTTPException(400, "Signup failed")


@router.post("/login")
def login(payload: LoginRequest, db=Depends(get_db)):
    try:
        logger.info(f"Login attempt for email: {payload.email} at /login endpoint")
        cursor, conn = db

        data = auth_login(cursor, conn, payload)
        return api_response(200, "Login successful", data=data)
    except Exception as e:
        logger.error(f"Login failed for email: {payload.email} with error: {str(e)}")
        raise HTTPException(401, "Login failed")

#refresh token sql model
@router.post("/refresh")
def refresh(payload: RefreshTokenRequest, db=Depends(get_db)):
    try:
        logger.info("Token refresh attempt at /refresh endpoint")
        cursor, conn = db

        data = auth_refresh(cursor, conn, payload.refresh_token)
        return api_response(200, "Token refreshed", data=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed with error: {str(e)}")
        raise HTTPException(500, "Token refresh failed")

@router.post("/logout")
def logout(db=Depends(get_db),user=Depends(get_current_user)):
    try:
        logger.info("Logout attempt at /logout endpoint")
        cursor, conn = db

        auth_logout(cursor, conn,user)
        return api_response(200, "Logout successful")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed with error: {str(e)}")
        raise HTTPException(500, "Logout failed")

@router.delete("/delete")
def delete_user_route(db=Depends(get_db),user=Depends(get_current_user),confirm: bool = False):
    try:
        logger.info(f"User deletion attempt for user_id: {user['id']} at /delete endpoint")
        cursor, conn = db
        data = delete_user(cursor, conn,user,confirm)
        return api_response(200, "none", data=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User account delete failed: {str(e)}")
        raise HTTPException(500, "user account delete failed")