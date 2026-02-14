from app.database.db_connection import get_connection
from app.utils.logger import logger

def get_db():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    logger.info(f"Database connection established")
    try:
        yield cursor, connection
        
    finally:
        cursor.close()
        connection.close()
        logger.info(f"Database connection closed")
