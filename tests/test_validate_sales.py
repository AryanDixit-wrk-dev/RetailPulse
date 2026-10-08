import pandas as pd

from validation.validate_sales import (
    get_duplicate_order_rows,
    get_invalid_category_rows,
    get_invalid_category_value_rows,
    get_invalid_order_date_format_rows,
    get_invalid_order_date_rows,
    get_invalid_order_id_rows,
    get_invalid_price_rows,
    get_invalid_price_value_rows,
    get_invalid_product_rows,
    get_invalid_quantity_rows,
    get_invalid_quantity_value_rows,
    get_invalid_sales_rows,
    get_missing_required_rows,
    get_sales_rejection_reasons,
    validate_sales_data,
    split_valid_invalid_sales,
)


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


def test_get_invalid_quantity_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", "B", "C"],
            "category": ["X", "X", "Y"],
            "quantity": [2, 0, -1],
            "price": [100, 200, 300],
            "order_date": [
                "2026-10-01",
                "2026-10-01",
                "2026-10-01",
            ],
        }
    )

    invalid_rows = get_invalid_quantity_rows(df)

    assert len(invalid_rows) == 2
    assert invalid_rows["order_id"].tolist() == [2, 3]

def test_get_invalid_price_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", "B", "C"],
            "category": ["X", "X", "Y"],
            "quantity": [2, 3, 4],
            "price": [100, 0, -50],
            "order_date": [
                "2026-10-01",
                "2026-10-01",
                "2026-10-01",
            ],
        }
    )

    invalid_rows = get_invalid_price_rows(df)

    assert len(invalid_rows) == 2
    assert invalid_rows["order_id"].tolist() == [2, 3]

def test_get_duplicate_order_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 2, 3],
            "product": ["A", "B", "B2", "C"],
            "category": ["X", "X", "X", "Y"],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
            ],
        }
    )

    duplicate_rows = get_duplicate_order_rows(df)

    assert len(duplicate_rows) == 2
    assert duplicate_rows["order_id"].tolist() == [2, 2]

def test_get_invalid_category_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", "B", "C"],
            "category": ["X", None, "Y"],
            "quantity": [2, 3, 4],
            "price": [100, 200, 300],
            "order_date": [
                "2026-10-01",
                "2026-10-01",
                "2026-10-01",
            ],
        }
    )

    invalid_rows = get_invalid_category_rows(df)

    assert len(invalid_rows) == 1
    assert invalid_rows["order_id"].tolist() == [2]

def test_get_invalid_order_date_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", "B", "C"],
            "category": ["X", "Y", "Z"],
            "quantity": [2, 3, 4],
            "price": [100, 200, 300],
            "order_date": [
                "2026-10-01",
                None,
                "2026-10-03",
            ],
        }
    )

    invalid_rows = get_invalid_order_date_rows(df)

    assert len(invalid_rows) == 1
    assert invalid_rows["order_id"].tolist() == [2]

def test_get_invalid_order_date_format_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", "B", "C"],
            "category": ["X", "Y", "Z"],
            "quantity": [2, 3, 4],
            "price": [100, 200, 300],
            "order_date": [
                "2026-10-01",
                "2026/10/02",
                "invalid-date",
            ],
        }
    )

    invalid_rows = get_invalid_order_date_format_rows(df)

    assert len(invalid_rows) == 2
    assert invalid_rows["order_id"].tolist() == [2, 3]

def test_get_missing_required_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", None, "C"],
            "category": ["X", "Y", "Z"],
            "quantity": [2, 3, 4],
            "price": [100, None, 300],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
            ],
        }
    )

    invalid_rows = get_missing_required_rows(df)

    assert len(invalid_rows) == 1
    assert invalid_rows["order_id"].tolist() == [2]

def test_get_invalid_order_id_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 0, -3, 4],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    invalid_rows = get_invalid_order_id_rows(df)

    assert len(invalid_rows) == 2
    assert invalid_rows["order_id"].tolist() == [0, -3]

def test_get_invalid_product_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "product": ["A", None, "", "   "],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    invalid_rows = get_invalid_product_rows(df)

    assert len(invalid_rows) == 3
    assert invalid_rows["order_id"].tolist() == [2, 3, 4]

def test_get_invalid_category_value_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "product": ["A", "B", "C", "D"],
            "category": ["X", None, "", "   "],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    invalid_rows = get_invalid_category_value_rows(df)

    assert len(invalid_rows) == 3
    assert invalid_rows["order_id"].tolist() == [2, 3, 4]

def test_get_invalid_quantity_value_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, None, "invalid", 3.5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    invalid_rows = get_invalid_quantity_value_rows(df)

    assert len(invalid_rows) == 3
    assert invalid_rows["order_id"].tolist() == [2, 3, 4]

def test_get_invalid_price_value_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, 3, 4, 5],
            "price": [100, None, "invalid", 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    invalid_rows = get_invalid_price_value_rows(df)

    assert len(invalid_rows) == 2
    assert invalid_rows["order_id"].tolist() == [2, 3]

def test_get_invalid_sales_rows():
    df = pd.DataFrame(
        {
            "order_id": [1, 0, 3, 4],
            "product": ["A", "B", None, "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, 3, 0, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "invalid-date",
            ],
        }
    )

    invalid_rows = get_invalid_sales_rows(df)

    assert len(invalid_rows) == 3
    assert invalid_rows["order_id"].tolist() == [0, 3, 4]

def test_get_sales_rejection_reasons():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4, 5],
            "product": ["A", "B", "C", "D", "E"],
            "category": ["X", "Y", "Z", "W", "V"],
            "quantity": [2, 0, 4, 5, 6],
            "price": [100, 200, 0, 400, 500],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "invalid-date",
                "2026-10-05",
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == ""
    assert reasons.iloc[1] == "Quantity must be greater than zero."
    assert reasons.iloc[2] == "Price must be greater than zero."
    assert reasons.iloc[3] == "Invalid order date."
    assert reasons.iloc[4] == ""

def test_get_sales_rejection_reasons_for_duplicates():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 2, 3],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == ""
    assert reasons.iloc[1] == "Duplicate order ID."
    assert reasons.iloc[2] == "Duplicate order ID."
    assert reasons.iloc[3] == ""

def test_get_sales_rejection_reasons_for_missing_values():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": [None, "B", "C"],
            "category": ["X", None, "Z"],
            "quantity": [2, 3, 4],
            "price": [100, 200, 300],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                None,
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == "Product is missing."
    assert reasons.iloc[1] == "Category is missing."
    assert reasons.iloc[2] == "Order date is missing."

def test_get_sales_rejection_reasons_for_order_id():
    df = pd.DataFrame(
        {
            "order_id": [None, 0, -2, 4],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == "Order ID is missing."
    assert reasons.iloc[1] == "Order ID must be greater than zero."
    assert reasons.iloc[2] == "Order ID must be greater than zero."
    assert reasons.iloc[3] == ""

def test_get_sales_rejection_reasons_for_empty_text():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "product": ["", "   ", "C", "D"],
            "category": ["X", "Y", "", "   "],
            "quantity": [2, 3, 4, 5],
            "price": [100, 200, 300, 400],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == "Product is missing."
    assert reasons.iloc[1] == "Product is missing."
    assert reasons.iloc[2] == "Category is missing."
    assert reasons.iloc[3] == "Category is missing."

def test_get_sales_rejection_reasons_for_quantity_and_price():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "product": ["A", "B", "C", "D"],
            "category": ["X", "Y", "Z", "W"],
            "quantity": [None, 0, 4, 5],
            "price": [100, 200, None, 0],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04",
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == "Quantity is missing."
    assert reasons.iloc[1] == "Quantity must be greater than zero."
    assert reasons.iloc[2] == "Price is missing."
    assert reasons.iloc[3] == "Price must be greater than zero."

def test_get_sales_rejection_reasons_for_multiple_errors():
    df = pd.DataFrame(
        {
            "order_id": [1, 2],
            "product": ["", "B"],
            "category": ["X", "Y"],
            "quantity": [0, 3],
            "price": [100, 200],
            "order_date": [
                "invalid-date",
                "2026-10-02",
            ],
        }
    )

    reasons = get_sales_rejection_reasons(df)

    assert reasons.iloc[0] == (
    "Product is missing.; Quantity must be greater than zero.; Invalid order date."
)
    assert reasons.iloc[1] == ""

def test_split_valid_invalid_sales():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "product": ["A", "", "C"],
            "category": ["X", "Y", "Z"],
            "quantity": [2, 0, 4],
            "price": [100, 200, 300],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
            ],
        }
    )

    valid_rows, invalid_rows, reasons = split_valid_invalid_sales(df)

    assert valid_rows["order_id"].tolist() == [1, 3]
    assert invalid_rows["order_id"].tolist() == [2]
    assert reasons.iloc[0] == (
    "Product is missing.; Quantity must be greater than zero."
)
