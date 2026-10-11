import os

from fastapi.testclient import TestClient

from api.main import app


API_KEY = os.getenv("API_KEY")

client = TestClient(app)

AUTH_HEADERS = {
    "X-API-Key": API_KEY,
}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_pipeline_health_endpoint():
    response = client.get(
        "/pipeline/health",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_runs" in data
    assert "successful_runs" in data
    assert "failed_runs" in data
    assert "skipped_runs" in data
    assert "latest_run_at" in data


def test_sales_summary_endpoint():
    response = client.get(
        "/sales/summary",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_sales" in data
    assert "total_orders" in data
    assert "total_quantity" in data
    assert float(data["total_sales"]) >= 0
    assert data["total_orders"] >= 0
    assert data["total_quantity"] >= 0


def test_sales_summary_date_filter():
    response = client.get(
        "/sales/summary",
        params={
            "start_date": "2026-10-10",
            "end_date": "2026-10-10",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == "113200.00"
    assert data["total_orders"] == 2
    assert data["total_quantity"] == 6


def test_sales_summary_product_filter():
    response = client.get(
        "/sales/summary",
        params={
            "products": "Laptop",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_sales" in data
    assert data["total_orders"] >= 0
    assert data["total_quantity"] >= 0


def test_sales_summary_category_filter():
    response = client.get(
        "/sales/summary",
        params={
            "categories": "Electronics",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_sales" in data
    assert data["total_orders"] >= 0
    assert data["total_quantity"] >= 0


def test_sales_summary_combined_filter():
    response = client.get(
        "/sales/summary",
        params=[
            ("start_date", "2026-10-10"),
            ("end_date", "2026-10-10"),
            ("products", "Laptop"),
            ("categories", "Electronics"),
        ],
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == "110000.00"
    assert data["total_orders"] == 1
    assert data["total_quantity"] == 2


def test_sales_by_product_endpoint():
    response = client.get(
        "/sales/by-product",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 8

    product_names = {
        row["product_name"]
        for row in data
    }

    assert "Laptop" in product_names
    assert "Mouse" in product_names

    for row in data:
        assert row["total_quantity"] >= 0
        assert float(row["total_sales"]) >= 0


def test_sales_by_product_date_filter():
    response = client.get(
        "/sales/by-product",
        params={
            "start_date": "2026-10-10",
            "end_date": "2026-10-10",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    product_names = {
        row["product_name"]
        for row in data
    }

    assert product_names == {"Laptop", "Mouse"}


def test_sales_by_product_filter():
    response = client.get(
        "/sales/by-product",
        params={
            "products": "Laptop",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["product_name"] == "Laptop"
    assert float(data[0]["total_sales"]) >= 0


def test_sales_by_category_endpoint():
    response = client.get(
        "/sales/by-category",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    category_names = {
        row["category_name"]
        for row in data
    }

    assert category_names == {
        "Electronics",
        "Accessories",
    }

    for row in data:
        assert row["total_quantity"] >= 0
        assert float(row["total_sales"]) >= 0


def test_sales_by_category_date_filter():
    response = client.get(
        "/sales/by-category",
        params={
            "start_date": "2026-10-10",
            "end_date": "2026-10-10",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    sales_by_category = {
        row["category_name"]: row["total_sales"]
        for row in data
    }

    assert sales_by_category["Electronics"] == "110000.00"
    assert sales_by_category["Accessories"] == "3200.00"


def test_sales_by_date_endpoint():
    response = client.get(
        "/sales/by-date",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 649

    date_keys = {
        row["date_key"]
        for row in data
    }

    assert 20250101 in date_keys
    assert 20261011 in date_keys

    for row in data:
        assert row["total_quantity"] >= 0
        assert float(row["total_sales"]) >= 0
        assert row["total_orders"] >= 0


def test_sales_by_date_product_filter():
    response = client.get(
        "/sales/by-date",
        params={
            "products": "Laptop",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 648

    for row in data:
        assert row["total_quantity"] >= 0
        assert float(row["total_sales"]) >= 0
        assert row["total_orders"] >= 0


def test_pipeline_runs_endpoint():
    response = client.get(
        "/pipeline/runs",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 10


def test_pipeline_runs_limit():
    response = client.get(
        "/pipeline/runs",
        params={"limit": 5},
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()) <= 5


def test_pipeline_runs_invalid_limit():
    response = client.get(
        "/pipeline/runs",
        params={"limit": 0},
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_pipeline_runs_max_limit():
    response = client.get(
        "/pipeline/runs",
        params={"limit": 101},
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_sales_predictions_endpoint():
    response = client.get(
        "/predictions/sales",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 8

    for row in data:
        assert "forecast_date" in row
        assert "product_name" in row
        assert "predicted_quantity" in row
        assert float(row["predicted_quantity"]) >= 0


def test_sales_predictions_products():
    response = client.get(
        "/predictions/sales",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    products = {
        row["product_name"]
        for row in data
    }

    assert products == {
        "Headphones",
        "Keyboard",
        "Laptop",
        "Monitor",
        "Mouse",
        "Tablet",
        "USB Hub",
        "Webcam",
    }


def test_sales_predictions_forecast_date():
    response = client.get(
        "/predictions/sales",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    forecast_dates = {
        row["forecast_date"]
        for row in data
    }

    assert len(forecast_dates) == 1
    assert "2026-10-09" in forecast_dates