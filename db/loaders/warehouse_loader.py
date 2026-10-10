import pandas as pd


def load_warehouse_data(
    df: pd.DataFrame,
    conn,
    pipeline_run_id: int,
) -> int:
    """Load sales data into the warehouse dimensions and fact table."""

    inserted_rows = 0

    with conn.cursor() as cursor:
        for row in df.itertuples(index=False):
            cursor.execute(
                """
                INSERT INTO dim_category (category_name)
                VALUES (%s)
                ON CONFLICT (category_name) DO NOTHING
                """,
                (row.category,),
            )

            cursor.execute(
                """
                SELECT category_key
                FROM dim_category
                WHERE category_name = %s
                """,
                (row.category,),
            )
            category_key = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO dim_product (product_name, category_key)
                VALUES (%s, %s)
                ON CONFLICT (product_name)
                DO UPDATE SET category_key = EXCLUDED.category_key
                """,
                (row.product, category_key),
            )

            cursor.execute(
                """
                SELECT product_key
                FROM dim_product
                WHERE product_name = %s
                """,
                (row.product,),
            )
            product_key = cursor.fetchone()[0]

            date_key = int(row.order_date.strftime("%Y%m%d"))

            cursor.execute(
                """
                INSERT INTO dim_date (
                    date_key,
                    full_date,
                    year,
                    month,
                    month_name,
                    quarter,
                    day,
                    day_of_week,
                    day_name
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (date_key) DO NOTHING
                """,
                (
                    date_key,
                    row.order_date,
                    row.order_date.year,
                    row.order_date.month,
                    row.order_date.strftime("%B"),
                    (row.order_date.month - 1) // 3 + 1,
                    row.order_date.day,
                    row.order_date.isoweekday(),
                    row.order_date.strftime("%A"),
                ),
            )

            cursor.execute(
                """
                INSERT INTO fact_sales (
                    order_id,
                    date_key,
                    product_key,
                    category_key,
                    quantity,
                    unit_price,
                    total_sales,
                    pipeline_run_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id)
                DO UPDATE SET
                    date_key = EXCLUDED.date_key,
                    product_key = EXCLUDED.product_key,
                    category_key = EXCLUDED.category_key,
                    quantity = EXCLUDED.quantity,
                    unit_price = EXCLUDED.unit_price,
                    total_sales = EXCLUDED.total_sales,
                    pipeline_run_id = EXCLUDED.pipeline_run_id
                """,
                (
                    row.order_id,
                    date_key,
                    product_key,
                    category_key,
                    row.quantity,
                    row.price,
                    row.quantity * row.price,
                    pipeline_run_id,
                ),
            )

            inserted_rows += 1

    conn.commit()
    return inserted_rows