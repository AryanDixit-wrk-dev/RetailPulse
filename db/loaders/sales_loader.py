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
                INSERT INTO sales (order_id, product, quantity, price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (order_id)
                DO UPDATE SET
                    product = EXCLUDED.product,
                    quantity = EXCLUDED.quantity,
                    price = EXCLUDED.price
                """,
                (
                    row.order_id,
                    row.product,
                    row.quantity,
                    row.price,
                ),
            )

            affected_rows += cursor.rowcount

    conn.commit()

    return affected_rows