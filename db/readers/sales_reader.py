import pandas as pd
import psycopg


def read_sales_from_database(
    conn: psycopg.Connection,
) -> pd.DataFrame:
    """Read all sales records from PostgreSQL."""

    query = """
        SELECT
            order_id,
            product,
            quantity,
            price
        FROM sales
        ORDER BY order_id;
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description.name for description in cursor.description]

    return pd.DataFrame(rows, columns=columns)