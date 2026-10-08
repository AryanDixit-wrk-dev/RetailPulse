import pandas as pd

from contracts.sales_contract import validate_sales_schema


def valid_sales_data():
    return pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )


def test_valid_sales_schema():
    df = valid_sales_data()

    errors = validate_sales_schema(df)

    assert errors == []


def test_missing_column():
    df = valid_sales_data().drop(columns=["category"])

    errors = validate_sales_schema(df)

    assert "Missing columns: ['category']" in errors


def test_invalid_order_id_type():
    df = valid_sales_data()
    df["order_id"] = df["order_id"].astype(str)

    errors = validate_sales_schema(df)

    assert "order_id must be an integer column." in errors


def test_invalid_quantity_type():
    df = valid_sales_data()
    df["quantity"] = df["quantity"].astype(float)

    errors = validate_sales_schema(df)

    assert "quantity must be an integer column." in errors


def test_invalid_price_type():
    df = valid_sales_data()
    df["price"] = ["high", "low"]

    errors = validate_sales_schema(df)

    assert "price must be a numeric column." in errors
