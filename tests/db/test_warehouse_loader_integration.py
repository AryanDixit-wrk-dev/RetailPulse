from db.connection import get_connection
from db.loaders.warehouse_loader import load_warehouse_data
from ingestion.load_csv import load_csv
from transformation.sales_transform import transform_sales_data


def test_warehouse_loader_integration():
    file_path = "data/raw/airflow_test_batch.csv"

    df = load_csv(file_path)

    df = df[df["quantity"] > 0].copy()
    df = transform_sales_data(df)

    conn = get_connection()

    try:
        loaded_rows = load_warehouse_data(
            df,
            conn,
            pipeline_run_id=174,
        )
    finally:
        conn.close()

    assert loaded_rows == 2
