from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.database.cursor_config import get_db
from app.middleware.auth_me import get_current_user
from app.services.audit_service import create_audit_log
from app.utils.logger import logger
from app.schemas.audit_schema import AuditCreate
router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])



@router.post("/create")
def create_audit(
    payload: AuditCreate,
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    cursor, connection = db

    result = create_audit_log(
        action=payload.action,
        entity_id=payload.entity_id,
        user_id=payload.user_id,
    )

    logger.info(f"Audit created by admin={user['id']}")
    return result
