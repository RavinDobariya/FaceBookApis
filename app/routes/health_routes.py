from fastapi import APIRouter, Depends
from app.database.cursor_config import get_db
from app.utils.response_handler import api_response
from app.utils.logger import logger
from fastapi import Request
router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(request: Request,db=Depends(get_db)):
    logger.info("Health check endpoint called")
    cursor, conn = db

    cursor.execute("SELECT 1 AS ok")
    result = cursor.fetchone()

    return api_response(status_code=200,message="Health check success",data=result)

