import pandas as pd

from transformation.sales_transform import transform_sales_data


def test_transform_sales_data_creates_expected_columns():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    result = transform_sales_data(df)

    assert "order_year" in result.columns
    assert "order_month" in result.columns
    assert "total_sales" in result.columns


def test_transform_sales_data_calculates_values():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    result = transform_sales_data(df)

    assert result["order_year"].tolist() == [2026, 2026]
    assert result["order_month"].tolist() == [9, 9]
    assert result["total_sales"].tolist() == [110000, 4000]


def test_transform_sales_data_converts_order_date():
    df = pd.DataFrame(
        {
            "order_id": [1001],
            "product": ["Laptop"],
            "category": ["Electronics"],
            "quantity": [2],
            "price": [55000],
            "order_date": ["2026-09-25"],
        }
    )

    result = transform_sales_data(df)

    assert pd.api.types.is_datetime64_any_dtype(
        result["order_date"]
    )

def test_transform_sales_data_calculates_order_quarter():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003, 1004],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "X", "Y", "Y"],
            "quantity": [1, 1, 1, 1],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-01-15",
                "2026-04-15",
                "2026-07-15",
                "2026-10-15",
            ],
        }
    )

    result = transform_sales_data(df)

    assert result["order_quarter"].tolist() == [1, 2, 3, 4]


def test_transform_sales_data_calculates_unit_price():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    result = transform_sales_data(df)

    assert result["unit_price"].tolist() == [55000, 800]

def test_transform_sales_data_strips_text_whitespace():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": [" Laptop ", "Mouse"],
            "category": [" Electronics ", " Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    result = transform_sales_data(df)

    assert result["product"].tolist() == ["Laptop", "Mouse"]
    assert result["category"].tolist() == ["Electronics", "Accessories"]