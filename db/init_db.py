from pathlib import Path

from db.connection import get_connection


def initialize_database():
    """Create the database tables from the SQL schema file."""

    schema_path = Path("sql/schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)

        conn.commit()
        print("Database schema initialized successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
