from datetime import datetime

from airflow.sdk import DAG, task


with DAG(
    dag_id="retailpulse_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    @task
    def run_pipeline():
        from pipeline.run_pipeline import run_sales_pipeline

        file_path = "/opt/retailpulse/data/raw/sample_sales.csv"

        success = run_sales_pipeline(file_path)

        if not success:
            raise RuntimeError("RetailPulse pipeline failed")

    run_pipeline()