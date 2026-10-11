from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from api.auth import verify_api_key
from api.main import app


client = TestClient(app)

API_KEY = "test-api-key"


@pytest.fixture(autouse=True)
def override_api_key():
    app.dependency_overrides[verify_api_key] = lambda: API_KEY
    yield
    app.dependency_overrides.clear()


def auth_headers():
    return {"X-API-Key": API_KEY}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_pipeline_health_endpoint(monkeypatch):
    def fake_get_connection():
        return None

    def fake_pipeline_health(conn):
        return {
            "total_runs": 10,
            "successful_runs": 9,
            "failed_runs": 1,
            "skipped_runs": 0,
            "latest_run_at": None,
        }

    monkeypatch.setattr(
        "api.routes.pipeline.get_db_connection",
        fake_get_connection,
    )
    monkeypatch.setattr(
        "api.routes.pipeline.get_pipeline_health",
        fake_pipeline_health,
    )

    response = client.get(
        "/pipeline/health",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_runs": 10,
        "successful_runs": 9,
        "failed_runs": 1,
        "skipped_runs": 0,
        "latest_run_at": None,
    }


def test_sales_summary_endpoint(monkeypatch):
    def fake_get_connection():
        return None

    def fake_sales_data(table_name, conn):
        assert table_name == "sales_summary"

        return [
            {
                "total_sales": Decimal("156700.00"),
                "total_orders": 4,
                "total_quantity": 11,
            }
        ]

    monkeypatch.setattr(
        "api.routes.sales.get_db_connection",
        fake_get_connection,
    )
    monkeypatch.setattr(
        "api.routes.sales.get_sales_data",
        fake_sales_data,
    )

    response = client.get(
        "/sales/summary",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_sales": "156700.00",
        "total_orders": 4,
        "total_quantity": 11,
    }


def test_sales_by_product_endpoint(monkeypatch):
    def fake_get_connection():
        return None

    def fake_sales_data(table_name, conn):
        assert table_name == "sales_by_product"

        return [
            {
                "product_key": 1,
                "total_quantity": 2,
                "total_sales": Decimal("110000.00"),
            }
        ]

    monkeypatch.setattr(
        "api.routes.sales.get_db_connection",
        fake_get_connection,
    )
    monkeypatch.setattr(
        "api.routes.sales.get_sales_data",
        fake_sales_data,
    )

    response = client.get(
        "/sales/by-product",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "product_key": 1,
            "total_quantity": 2,
            "total_sales": "110000.00",
        }
    ]


def test_sales_by_category_endpoint(monkeypatch):
    def fake_get_connection():
        return None

    def fake_sales_data(table_name, conn):
        assert table_name == "sales_by_category"

        return [
            {
                "category_key": 1,
                "total_quantity": 4,
                "total_sales": Decimal("146000.00"),
            }
        ]

    monkeypatch.setattr(
        "api.routes.sales.get_db_connection",
        fake_get_connection,
    )
    monkeypatch.setattr(
        "api.routes.sales.get_sales_data",
        fake_sales_data,
    )

    response = client.get(
        "/sales/by-category",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "category_key": 1,
            "total_quantity": 4,
            "total_sales": "146000.00",
        }
    ]


def test_sales_by_date_endpoint(monkeypatch):
    def fake_get_connection():
        return None

    def fake_sales_data(table_name, conn):
        assert table_name == "sales_by_date"

        return [
            {
                "date_key": 20261010,
                "total_quantity": 6,
                "total_sales": Decimal("113200.00"),
                "total_orders": 2,
            }
        ]

    monkeypatch.setattr(
        "api.routes.sales.get_db_connection",
        fake_get_connection,
    )
    monkeypatch.setattr(
        "api.routes.sales.get_sales_data",
        fake_sales_data,
    )

    response = client.get(
        "/sales/by-date",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "date_key": 20261010,
            "total_quantity": 6,
            "total_sales": "113200.00",
            "total_orders": 2,
        }
    ]


def test_pipeline_runs_endpoint(monkeypatch):
    def fake_get_connection():
        return None

    def fake_recent_pipeline_runs(conn, limit):
        assert limit == 10

        return [
            {
                "run_id": 100,
                "pipeline_name": "sales_pipeline",
                "source_file": "sales.csv",
                "status": "SUCCESS",
                "started_at": datetime(2026, 10, 11, 10, 0),
                "completed_at": datetime(2026, 10, 11, 10, 1),
                "records_received": 10,
                "records_accepted": 9,
                "records_rejected": 1,
                "records_processed": 9,
                "error_message": None,
            }
        ]

    monkeypatch.setattr(
        "api.routes.pipeline.get_db_connection",
        fake_get_connection,
    )
    monkeypatch.setattr(
        "api.routes.pipeline.get_recent_pipeline_runs",
        fake_recent_pipeline_runs,
    )

    response = client.get(
        "/pipeline/runs",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "run_id": 100,
            "pipeline_name": "sales_pipeline",
            "source_file": "sales.csv",
            "status": "SUCCESS",
            "started_at": "2026-10-11T10:00:00",
            "completed_at": "2026-10-11T10:01:00",
            "records_received": 10,
            "records_accepted": 9,
            "records_rejected": 1,
            "records_processed": 9,
            "error_message": None,
        }
    ]
def test_pipeline_endpoint_rejects_missing_api_key():
    app.dependency_overrides.clear()

    response = client.get("/pipeline/health")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API key."
    }


def test_pipeline_endpoint_rejects_invalid_api_key():
    app.dependency_overrides.clear()

    response = client.get(
        "/pipeline/health",
        headers={"X-API-Key": "wrong-api-key"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or missing API key."
    }