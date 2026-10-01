from datetime import datetime

from airflow.sdk import DAG, task


with DAG(
    dag_id="retailpulse_test",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    @task
    def test_retailpulse():
        print("RetailPulse Airflow test successful!")


    test_retailpulse()