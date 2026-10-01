# RetailPulse

RetailPulse is an end-to-end sales data engineering and analytics platform.

## Architecture

CSV -> Ingestion -> Data Quality & Validation -> Transformation -> PostgreSQL -> dbt -> Analytics & Reports -> Airflow -> Power BI

## Core Components

- Python sales pipeline
- PostgreSQL database
- Data quality and validation
- dbt staging, intermediate, and mart models
- Apache Airflow orchestration
- Power BI dashboard
- Automated Python tests
- Docker-based Airflow environment

## Testing

Run the Python test suite:

`python -m pytest -q`

Current result: 40 passed.

## Airflow

Start Airflow with:

`docker compose --env-file .\.env -f .\airflow\docker-compose.yml up -d`

DAG: `retailpulse_pipeline`

## dbt

Project: `dbt/retailpulse_dbt/`

Run:

`cd dbt/retailpulse_dbt`

`dbt build`

## Power BI

Dashboard: `reports/RetailPulse_Sales_Dashboard.pbix`

Dashboard includes sales KPIs, category analysis, product analysis, quantity analysis, sales trend, category filtering, and date filtering.

## Security

Environment files, generated Airflow configuration, logs, generated data, and other local artifacts are excluded from version control where appropriate.


