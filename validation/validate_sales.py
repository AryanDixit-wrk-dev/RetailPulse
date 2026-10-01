import pandas as pd


def validate_sales_data(df: pd.DataFrame) -> list[str]:
    """
    Validate the basic structure and values of sales data.

    Returns:
        A list of validation errors.
        An empty list means the data passed validation.
    """

    errors = []

    required_columns = [
        "order_id",
        "product",
        "category",
        "quantity",
        "price",
        "order_date",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
        return errors

    if df[required_columns].isnull().any().any():
        errors.append("Missing values found in required columns.")

    if (df["quantity"] <= 0).any():
        errors.append("Quantity must be greater than zero.")

    if (df["price"] <= 0).any():
        errors.append("Price must be greater than zero.")

    if df["order_id"].duplicated().any():
        errors.append("Duplicate order_id values found.")

    if df["category"].isnull().any():
        errors.append("Category cannot be missing.")

    if df["order_date"].isnull().any():
        errors.append("Order date cannot be missing.")

    try:
        pd.to_datetime(df["order_date"], errors="raise")
    except (ValueError, TypeError):
        errors.append("Invalid order_date values found.")

    return errors
