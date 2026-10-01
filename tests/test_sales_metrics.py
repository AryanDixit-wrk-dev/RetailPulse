import pandas as pd

from analytics.sales_metrics import (
    calculate_sales_metrics,
    sales_by_product,
    sales_by_category,
)

def test_calculate_sales_metrics():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "quantity": [2, 5, 3],
            "price": [55000, 800, 1500],
        }
    )

    metrics = calculate_sales_metrics(df)

    assert metrics["total_orders"] == 3
    assert metrics["total_quantity"] == 10
    assert metrics["total_sales"] == 118500.0
    assert metrics["average_order_value"] == 39500.0


def test_empty_sales_data():
    df = pd.DataFrame(
        {
            "order_id": pd.Series(dtype="int64"),
            "product": pd.Series(dtype="object"),
            "quantity": pd.Series(dtype="int64"),
            "price": pd.Series(dtype="float64"),
        }
    )

    metrics = calculate_sales_metrics(df)

    assert metrics["total_orders"] == 0
    assert metrics["total_quantity"] == 0
    assert metrics["total_sales"] == 0.0
    assert metrics["average_order_value"] == 0.0


def test_single_order():
    df = pd.DataFrame(
        {
            "order_id": [1001],
            "product": ["Laptop"],
            "quantity": [2],
            "price": [55000],
        }
    )

    metrics = calculate_sales_metrics(df)

    assert metrics["total_orders"] == 1
    assert metrics["total_quantity"] == 2
    assert metrics["total_sales"] == 110000.0
    assert metrics["average_order_value"] == 110000.0

def test_sales_by_product():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Laptop"],
            "quantity": [2, 5, 1],
            "price": [55000, 800, 55000],
        }
    )

    result = sales_by_product(df)

    laptop = result[result["product"] == "Laptop"].iloc[0]

    assert laptop["total_quantity"] == 3
    assert laptop["total_sales"] == 165000
    assert laptop["total_orders"] == 2

def test_sales_by_category():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "category": ["Electronics", "Accessories", "Accessories"],
            "quantity": [2, 5, 3],
            "price": [55000, 800, 1500],
        }
    )

    result = sales_by_category(df)

    accessories = result[
        result["category"] == "Accessories"
    ].iloc[0]

    assert accessories["total_quantity"] == 8
    assert accessories["total_sales"] == 8500
    assert accessories["total_orders"] == 2