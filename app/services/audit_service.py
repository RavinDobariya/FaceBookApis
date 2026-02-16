import uuid
from app.utils.logger import logger,log_exception
from fastapi import HTTPException
from app.utils.response_handler import api_response
from app.database.cursor_config import get_db,get_connection
from fastapi.params import Depends




def create_audit_log(action: str, entity_id: str, user_id: str):
    """
    Create audit logs synchronously during request (PDF requirement).
    Logs who did what action on which entity.
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        audit_id = uuid.uuid4()
        audit_id_str = f"{audit_id}"
        cursor.execute(
            """
            INSERT INTO audit_log (id, action, entity_id, user_id)
            VALUES (%s, %s, %s, %s)
            """,
            (audit_id_str, action, entity_id, user_id),
        )
        connection.commit()

        logger.info(f"Audit log created action={action} entity_id={entity_id} user_id={user_id}")
        return {"status_code": "success", "message": "Audit created"}


    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit log failed: {e}")
        raise HTTPException(500, detail="Failed to create audit logs")
