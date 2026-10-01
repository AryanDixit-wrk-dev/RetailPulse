from db.connection import get_connection


def test_database_connection():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()

        assert result == (1,)
    finally:
        conn.close()
