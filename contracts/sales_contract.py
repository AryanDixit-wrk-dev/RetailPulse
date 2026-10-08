import pandas as pd
from pandas.api.types import (
    is_integer_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)


REQUIRED_COLUMNS = [
    "order_id",
    "product",
    "category",
    "quantity",
    "price",
    "order_date",
]


def validate_sales_schema(df: pd.DataFrame) -> list[str]:
    """
    Validate the structural schema of incoming sales data.

    Returns:
        A list of schema errors.
        An empty list means the schema passed validation.
    """

    errors = []

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
        return errors

    if not is_integer_dtype(df["order_id"]):
        errors.append("order_id must be an integer column.")

    if not (
        is_string_dtype(df["product"])
        or is_object_dtype(df["product"])
    ):
        errors.append("product must be a string column.")

    if not (
        is_string_dtype(df["category"])
        or is_object_dtype(df["category"])
    ):
        errors.append("category must be a string column.")

    if not is_integer_dtype(df["quantity"]):
        errors.append("quantity must be an integer column.")

    if not is_numeric_dtype(df["price"]):
        errors.append("price must be a numeric column.")

    if not (
        is_string_dtype(df["order_date"])
        or is_object_dtype(df["order_date"])
    ):
        errors.append("order_date must be a date-compatible string column.")

    return errors
