import pandas as pd
from datetime import date
from decimal import Decimal
from db.connection import get_connection
from db.loaders.sales_loader import load_sales_to_database


def test_sales_loader_assigns_pipeline_run_id():
    df = pd.DataFrame(
        {
            "order_id": [900001],
            "product": ["Test Product"],
            "category": ["Test Category"],
            "quantity": [2],
            "price": [100],
            "order_date": ["2026-10-02"],
        }
    )

    conn = get_connection()

    try:
        load_sales_to_database(
            df,
            conn,
            pipeline_run_id=999999,
        )

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    order_id,
                    pipeline_run_id
                FROM sales
                WHERE order_id = %s;
                """,
                (900001,),
            )

            result = cursor.fetchone()

        assert result == (900001, 999999)

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sales WHERE order_id = %s;",
                (900001,),
            )
        conn.commit()
        conn.close()
def test_sales_loader_updates_existing_order_with_new_pipeline_run_id():
    df = pd.DataFrame(
        {
            "order_id": [900002],
            "product": ["Original Product"],
            "category": ["Test Category"],
            "quantity": [1],
            "price": [100],
            "order_date": ["2026-10-01"],
        }
    )

    conn = get_connection()

    try:
        load_sales_to_database(
            df,
            conn,
            pipeline_run_id=100001,
        )

        updated_df = pd.DataFrame(
            {
                "order_id": [900002],
                "product": ["Updated Product"],
                "category": ["Test Category"],
                "quantity": [5],
                "price": [500],
                "order_date": ["2026-10-02"],
            }
        )

        load_sales_to_database(
            updated_df,
            conn,
            pipeline_run_id=100002,
        )

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    product,
                    quantity,
                    price,
                    order_date,
                    pipeline_run_id
                FROM sales
                WHERE order_id = %s;
                """,
                (900002,),
            )

            result = cursor.fetchone()

        assert result == (
    "Updated Product",
    5,
    Decimal("500.00"),
    date(2026, 10, 2),
    100002,
)

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sales WHERE order_id = %s;",
                (900002,),
            )

        conn.commit()
        conn.close()