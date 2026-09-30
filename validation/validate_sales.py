import pandas as pd


def validate_sales_data(df: pd.DataFrame) -> list[str]:
    """
    Validate the basic structure and values of sales data.

    Returns:
        A list of validation errors.
        An empty list means the data passed validation.
    """
    errors = []

    required_columns = ["order_id", "product", "quantity", "price"]

    # Check required columns
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")

    # Stop here if required columns are missing
    if missing_columns:
        return errors

    # Check missing values
    if df[required_columns].isnull().any().any():
        errors.append("Missing values found in required columns.")

    # Check quantity
    if (df["quantity"] <= 0).any():
        errors.append("Quantity must be greater than zero.")

    # Check price
    if (df["price"] <= 0).any():
        errors.append("Price must be greater than zero.")
    # Check duplicate order IDs
    if df["order_id"].duplicated().any():
        errors.append("Duplicate order_id values found.")
        
    return errors