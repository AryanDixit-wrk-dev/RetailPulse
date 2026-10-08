import pandas as pd

from db.connection import get_connection
from db.loaders.quarantine_loader import load_quarantine_records


def test_load_quarantine_records():
    conn = get_connection()

    df = pd.DataFrame(
        [
            {
                "order_id": 900001,
                "product": "Test Product",
                "category": "Test",
                "quantity": 0,
                "price": 100,
                "order_date": "2026-10-07",
            }
        ]
    )

    try:
        inserted_rows = load_quarantine_records(
            df,
            conn,
            pipeline_run_id=999998,
            source_file="test_quarantine.csv",
            rejection_reason="Quantity must be greater than zero.",
        )

        assert inserted_rows == 1

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    pipeline_run_id,
                    source_file,
                    order_id,
                    rejection_reason
                FROM sales_quarantine
                WHERE pipeline_run_id = %s
                """,
                (999998,),
            )

            row = cursor.fetchone()

        assert row is not None
        assert row[0] == 999998
        assert row[1] == "test_quarantine.csv"
        assert row[2] == 900001
        assert row[3] == "Quantity must be greater than zero."

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM sales_quarantine
                WHERE pipeline_run_id = %s
                """,
                (999998,),
            )
        conn.commit()
        conn.close()
