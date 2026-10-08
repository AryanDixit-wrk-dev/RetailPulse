from db.connection import get_connection


def test_sales_table_schema():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'sales';
                """
            )

            rows = cursor.fetchall()

        actual_schema = {
            row[0]: (row[1], row[2])
            for row in rows
        }

        expected_schema = {
            "order_id": ("integer", "NO"),
            "product": ("text", "NO"),
            "category": ("text", "NO"),
            "quantity": ("integer", "NO"),
            "price": ("numeric", "NO"),
            "order_date": ("date", "NO"),
            "pipeline_run_id": ("bigint", "YES"),
        }

        assert actual_schema == expected_schema

    finally:
        conn.close()


def test_sales_price_precision():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT numeric_precision, numeric_scale
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'sales'
                  AND column_name = 'price';
                """
            )

            result = cursor.fetchone()

        assert result == (12, 2)

    finally:
        conn.close()