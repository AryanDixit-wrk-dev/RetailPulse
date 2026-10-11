import os

import requests
from dotenv import load_dotenv


load_dotenv()


API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")


def get_headers():
    return {
        "X-API-Key": API_KEY,
    }


def build_params(
    start_date=None,
    end_date=None,
    products=None,
    categories=None,
):
    params = []

    if start_date is not None:
        params.append(("start_date", start_date))

    if end_date is not None:
        params.append(("end_date", end_date))

    if products:
        params.extend(
            ("products", product)
            for product in products
        )

    if categories:
        params.extend(
            ("categories", category)
            for category in categories
        )

    return params


def get_sales_summary(
    start_date=None,
    end_date=None,
    products=None,
    categories=None,
):
    response = requests.get(
        f"{API_URL}/sales/summary",
        headers=get_headers(),
        params=build_params(
            start_date,
            end_date,
            products,
            categories,
        ),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_sales_by_product(
    start_date=None,
    end_date=None,
    products=None,
    categories=None,
):
    response = requests.get(
        f"{API_URL}/sales/by-product",
        headers=get_headers(),
        params=build_params(
            start_date,
            end_date,
            products,
            categories,
        ),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_sales_by_category(
    start_date=None,
    end_date=None,
    products=None,
    categories=None,
):
    response = requests.get(
        f"{API_URL}/sales/by-category",
        headers=get_headers(),
        params=build_params(
            start_date,
            end_date,
            products,
            categories,
        ),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_sales_by_date(
    start_date=None,
    end_date=None,
    products=None,
    categories=None,
):
    response = requests.get(
        f"{API_URL}/sales/by-date",
        headers=get_headers(),
        params=build_params(
            start_date,
            end_date,
            products,
            categories,
        ),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_pipeline_health():
    response = requests.get(
        f"{API_URL}/pipeline/health",
        headers=get_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_pipeline_runs(limit=10):
    response = requests.get(
        f"{API_URL}/pipeline/runs",
        headers=get_headers(),
        params={"limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()