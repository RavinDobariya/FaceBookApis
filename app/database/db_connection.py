import mysql.connector
from mysql.connector import Error
from app.utils.config import settings


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            port=settings.DB_PORT,
        )
        return connection
    except Error as e:
        # You can log this later using logger
        raise Exception(f"Database connection error: {e}")