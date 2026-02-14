from fastapi import HTTPException, Depends
from app.utils.security import create_access_token, create_refresh_token, verify_password
from app.utils.logger import logger,log_exception
from app.utils.security import hash_password
import uuid

ALLOWED_ROLES = {"admin", "user"}


def auth_signup(cursor, conn, payload):
    try:
        # role validate
        if payload.role not in ALLOWED_ROLES:
            logger.warning(f"Signup attempt with invalid role: {payload.role}") 
            raise HTTPException(400, "Invalid role")


        # email exists?
        cursor.execute("SELECT 1 FROM `user` WHERE email=%s", [payload.email])
        if cursor.fetchone():
            logger.warning(f"Signup attempt with existing email: {payload.email}")
            raise HTTPException(400, "Email already registered")

        while True:
            user_id = str(uuid.uuid4())

            cursor.execute("SELECT 1 FROM user WHERE id = %s LIMIT 1",(user_id,))

            exists = cursor.fetchone()
            if exists:
                logger.info("uuid generating again Bcuz duplicate found!!")
            else:
                break
        
        hashed_pass =hash_password(payload.password)    
        cursor.execute(
            "INSERT INTO `user` (id, email, password_hash, role) VALUES (%s,%s,%s,%s)",
            (user_id, payload.email, hashed_pass, payload.role)
        )
        conn.commit()
        logger.info(f"User signed up with email: user_id: {user_id},{payload.email}")

        return {"id": user_id, "email": payload.email, "role": payload.role}
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Error during signup for email: {payload.email}")
        raise HTTPException(500, "Signup failed")


def auth_login(cursor, conn, payload):
    try:
        cursor.execute( "SELECT id, email, password_hash, role FROM `user` WHERE email=%s",[payload.email])
        user = cursor.fetchone()

        if not user:
            logger.warning(f"Login attempt with invalid email: {payload.email}")
            raise HTTPException(status_code=404, detail="Invalid email")

        result = verify_password(payload.password,user["password_hash"])
        if not result:
            logger.warning(f"Login attempt with invalid password for email: {payload.email}")
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_access_token({   
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
        })
        refresh_token = create_refresh_token()
        
        cursor.execute(
            "INSERT INTO refresh_token (token, user_id) VALUES (%s, %s)",
            (refresh_token, user["id"])
        )
        conn.commit()
        logger.info(f"User logged in: user_id: {user['id']}, email: {payload.email}")

        return {"access_token": access_token,"refresh_token": refresh_token,"token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Auth Login Failed | email={payload.email}")
        raise HTTPException(500, "Login failed")

#todo: take refresh token from header
def auth_refresh(cursor, conn, refresh_token: str):
    try:
        cursor.execute("SELECT token, user_id, is_revoked FROM refresh_token WHERE token=%s",[refresh_token])
        token = cursor.fetchone()

        if not token:
            logger.warning("Token refresh attempt with invalid refresh token")
            raise HTTPException(401, "Invalid refresh token")

        if token["is_revoked"] == 1:
            
            
            logger.warning("Token refresh attempt with revoked refresh token")
            raise HTTPException(401, "Refresh token revoked")

        #fetching user details
        cursor.execute("SELECT id, email, role FROM `user` WHERE id=%s",[token["user_id"]])
        user = cursor.fetchone()

        if not user:
            logger.warning(f"User not found for refresh token: {refresh_token}")
            raise HTTPException(401, "User not found")

        # create new access token
        new_access_token = create_access_token({
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
        })

        return {"access_token": new_access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Error during token refresh error | {refresh_token}")
        raise HTTPException(500, "Token refresh failed")
    
def auth_logout(cursor, conn,user):
    try:
        user_id = user["id"]
        cursor.execute("SELECT is_revoked FROM refresh_token WHERE user_id=%s",[user_id])
        rows = cursor.fetchall()

        if not rows:
            logger.warning("Logout attempt with invalid refresh token")
            raise HTTPException(401, "Invalid refresh token")

        token_row = all(r["is_revoked"] == 1 for r in rows)
        
        if token_row:
            logger.warning("Logout attempt with already revoked refresh token")
            raise HTTPException (status_code=401, detail="Already logged out")                        # already logged out

        cursor.execute("UPDATE refresh_token SET is_revoked=1 WHERE user_id=%s",[user_id])
        conn.commit()
        logger.info(f"User logged out successfully for {user}")
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e,f"Error during logout | {user_id}")
        raise HTTPException(500, "Logout failed")


def delete_user(cursor, connection,user,confirm: bool ):
    try:
        if not confirm:
            return (
                "Deleting this user will remove all related data. Please confirm.",
                {"confirm_required": True}
            )
        cursor.execute("DELETE from `user` WHERE id=%s ",(user["id"],))
        connection.commit()

        return { "message": f"User deleted successfully {user['id']}"}

    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        log_exception(e,f"Delete user failed")
        raise HTTPException(status_code=500, detail="Failed to delete user")
