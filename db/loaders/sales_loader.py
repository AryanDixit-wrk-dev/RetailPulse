import pandas as pd
import psycopg


def load_sales_to_database(
    df: pd.DataFrame,
    conn: psycopg.Connection,
) -> int:
    """
    Insert new sales records or update existing records.

    Returns:
        Number of rows inserted or updated.
    """

    affected_rows = 0

    with conn.cursor() as cursor:
        for row in df.itertuples(index=False):
            cursor.execute(
                """
                INSERT INTO sales (
                    order_id,
                    product,
                    category,
                    quantity,
                    price,
                    order_date
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id)
                DO UPDATE SET
                    product = EXCLUDED.product,
                    category = EXCLUDED.category,
                    quantity = EXCLUDED.quantity,
                    price = EXCLUDED.price,
                    order_date = EXCLUDED.order_date
                """,
                (
                    row.order_id,
                    row.product,
                    row.category,
                    row.quantity,
                    row.price,
                    row.order_date,
                ),
            )

            affected_rows += cursor.rowcount

    conn.commit()

    return affected_rows