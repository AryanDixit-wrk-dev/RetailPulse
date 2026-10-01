import pandas as pd

from validation.validate_sales import validate_sales_data


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


def test_valid_sales_data():
    df = valid_sales_data()

    errors = validate_sales_data(df)

    assert errors == []


def test_missing_required_column():
    df = valid_sales_data().drop(columns=["category"])

    errors = validate_sales_data(df)

    assert "Missing columns: ['category']" in errors


def test_missing_values():
    df = valid_sales_data()
    df.loc[0, "product"] = None

    errors = validate_sales_data(df)

    assert "Missing values found in required columns." in errors


def test_invalid_quantity():
    df = valid_sales_data()
    df.loc[0, "quantity"] = 0

    errors = validate_sales_data(df)

    assert "Quantity must be greater than zero." in errors


def test_invalid_price():
    df = valid_sales_data()
    df.loc[0, "price"] = -100

    errors = validate_sales_data(df)

    assert "Price must be greater than zero." in errors


def test_duplicate_order_id():
    df = valid_sales_data()
    df.loc[1, "order_id"] = 1001

    errors = validate_sales_data(df)

    assert "Duplicate order_id values found." in errors


def test_missing_category():
    df = valid_sales_data()
    df.loc[0, "category"] = None

    errors = validate_sales_data(df)

    assert "Missing values found in required columns." in errors
    assert "Category cannot be missing." in errors


def test_missing_order_date():
    df = valid_sales_data()
    df.loc[0, "order_date"] = None

    errors = validate_sales_data(df)

    assert "Missing values found in required columns." in errors
    assert "Order date cannot be missing." in errors


def test_invalid_order_date():
    df = valid_sales_data()
    df.loc[0, "order_date"] = "not-a-date"

    errors = validate_sales_data(df)

    assert "Invalid order_date values found." in errors
