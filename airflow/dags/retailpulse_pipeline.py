from datetime import datetime
from pathlib import Path

from airflow.sdk import DAG, task


DBT_PROJECT_DIR = "/opt/retailpulse/dbt/retailpulse_dbt"


with DAG(
    dag_id="retailpulse_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["retailpulse", "sales"],
    default_args={
        "retries": 2,
    },
) as dag:

    @task
    def run_pipeline():
        from pipeline.run_pipeline import run_sales_pipeline
        from db.connection import get_connection
        from db.pipeline_runs import (
            calculate_file_hash,
            pipeline_run_exists,
        )

        raw_dir = Path("/opt/retailpulse/data/raw")

        csv_files = sorted(
            raw_dir.glob("*.csv"),
            key=lambda file: file.stat().st_mtime,
            reverse=True,
        )

        if not csv_files:
            raise FileNotFoundError(
                "No CSV files found in the raw data directory."
            )

        conn = get_connection()

        try:
            selected_file = None

            for file_path in csv_files:
                source_hash = calculate_file_hash(str(file_path))

                if not pipeline_run_exists(
                    conn,
                    pipeline_name="sales_pipeline",
                    source_hash=source_hash,
                ):
                    selected_file = file_path
                    break
        finally:
            conn.close()

        if selected_file is None:
            return "No new CSV files to process."

        success = run_sales_pipeline(str(selected_file))

        if not success:
            raise RuntimeError("RetailPulse pipeline failed")

        return f"Processed: {selected_file.name}"

    @task.bash
    def run_dbt():
        return (
            "dbt run "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROJECT_DIR}"
        )

    @task.bash
    def test_dbt():
        return (
            "dbt test "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROJECT_DIR}"
        )

    pipeline = run_pipeline()
    dbt_run = run_dbt()
    dbt_test = test_dbt()

    pipeline >> dbt_run >> dbt_test