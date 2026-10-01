from pathlib import Path

import pandas as pd
import psycopg


SQL_DIR = Path(__file__).resolve().parent.parent / "sql" / "analytics"


def get_sales_summary(
    conn: psycopg.Connection,
) -> dict:
    """Execute the sales summary SQL query and return the result."""

    sql_file = SQL_DIR / "sales_summary.sql"
    query = sql_file.read_text(encoding="utf-8")

    with conn.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        columns = [description.name for description in cursor.description]

    result = pd.Series(row, index=columns)

    return result.to_dict()


def get_sales_by_product(
    conn: psycopg.Connection,
) -> pd.DataFrame:
    """Execute the product sales SQL query."""

    sql_file = SQL_DIR / "sales_by_product.sql"
    query = sql_file.read_text(encoding="utf-8")

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [
            description.name
            for description in cursor.description
        ]

    return pd.DataFrame(rows, columns=columns)

def get_sales_by_category(
    conn: psycopg.Connection,
) -> pd.DataFrame:
    """Execute the category sales SQL query."""

    sql_file = SQL_DIR / "sales_by_category.sql"
    query = sql_file.read_text(encoding="utf-8")

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [
            description.name
            for description in cursor.description
        ]

    return pd.DataFrame(rows, columns=columns)

def get_sales_by_date(
    conn: psycopg.Connection,
) -> pd.DataFrame:
    """Execute the daily sales SQL query."""

    sql_file = SQL_DIR / "sales_by_date.sql"
    query = sql_file.read_text(encoding="utf-8")

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [
            description.name
            for description in cursor.description
        ]

    return pd.DataFrame(rows, columns=columns)