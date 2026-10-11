# RetailPulse

RetailPulse is an end-to-end sales data engineering, analytics, and machine learning platform.

The project ingests sales data, validates and transforms it, loads it into PostgreSQL, builds analytics models with dbt, orchestrates the workflow with Apache Airflow, exposes analytics and prediction APIs through FastAPI, and provides a Streamlit decision-support dashboard.

## Architecture

CSV
-> Ingestion
-> Data Quality & Validation
-> Transformation
-> PostgreSQL
-> dbt
-> Analytics & Reports
-> Machine Learning
-> FastAPI
-> Streamlit
-> Airflow Orchestration

## Core Components

- Python sales pipeline
- CSV ingestion and data validation
- Data contracts and data quality checks
- PostgreSQL operational and warehouse schemas
- Star-schema warehouse with fact and dimension tables
- dbt staging, intermediate, and mart models
- Apache Airflow orchestration
- FastAPI analytics and prediction API
- API-key authentication
- Streamlit dashboard
- Demand forecasting with Random Forest
- Model evaluation and baseline comparison
- Feature importance and model diagnostics
- Data drift monitoring
- Controlled model retraining and promotion workflow
- Pipeline logging and observability
- Automated Python tests
- Docker-based Airflow environment
- GitHub Actions CI validation

## Data Engineering Pipeline

The sales pipeline performs:

1. CSV ingestion
2. Data contract validation
3. Data quality checks
4. Invalid-record quarantine
5. Data transformation
6. PostgreSQL loading
7. Warehouse loading
8. Analytics report generation
9. Pipeline-run tracking and idempotency

Pipeline runs are tracked with source hashing and run metadata to prevent duplicate processing.

## Data Warehouse

RetailPulse uses PostgreSQL with a warehouse-oriented star schema.

### Main warehouse tables

- `fact_sales`
- `dim_product`
- `dim_category`
- `dim_date`

Pipeline execution metadata is stored separately in `pipeline_runs`.

## dbt

The dbt project is located at:

`dbt/retailpulse_dbt/`

The project contains:

- Staging models
- Intermediate models
- Mart models
- Source definitions
- Schema tests
- Custom data tests

Run:

```powershell
cd dbt/retailpulse_dbt
dbt build