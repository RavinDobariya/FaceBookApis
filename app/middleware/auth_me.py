from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.cursor_config import get_db
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),db=Depends(get_db)):
    cursor, conn = db
    token = creds.credentials

    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")

    cursor.execute("SELECT id, email, role FROM `user` WHERE id=%s ",[user_id])
    user = cursor.fetchone()

    if not user:
        raise HTTPException(401, "User not found")

    cursor.execute("SELECT 1 FROM refresh_token WHERE user_id=%s AND is_revoked=0 LIMIT 1",(user_id,))
    active_session = cursor.fetchone()

    if not active_session:
        raise HTTPException(status_code=401, detail="Logged out / Session expired")

    return user                 # userid, email, role

def auth_role(required_roles: list[str] | str):
    def role_checker(user=Depends(get_current_user)):
        role = user["role"].upper()
        if role not in required_roles:
            raise HTTPException(403, "permissions denied || ONLY ADMIN CAN ACCESS THIS ENDPOINT")
        return user
    return role_checker

