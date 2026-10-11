from fastapi import HTTPException

from db.connection import get_connection


def get_db_connection():
    try:
        return get_connection()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database service is unavailable.",
        ) from exc