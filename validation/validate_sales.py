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
        pd.to_datetime(
            df["order_date"],
            format="%Y-%m-%d",
            errors="raise",
        )
    except (ValueError, TypeError):
        errors.append("Invalid order_date values found.")

    return errors


def get_invalid_quantity_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where quantity is invalid."""

    return df[df["quantity"] <= 0].copy()


def get_invalid_price_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where price is invalid."""

    return df[df["price"] <= 0].copy()


def get_duplicate_order_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows with duplicate order IDs."""

    return df[df["order_id"].duplicated(keep=False)].copy()


def get_invalid_category_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where category is missing."""

    return df[df["category"].isna()].copy()


def get_invalid_order_date_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where order_date is missing."""

    return df[df["order_date"].isna()].copy()


def get_invalid_order_date_format_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows with invalid order_date values."""

    parsed_dates = pd.to_datetime(
        df["order_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    return df[
        df["order_date"].notna() & parsed_dates.isna()
    ].copy()


def get_missing_required_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows with missing values in required columns."""

    required_columns = [
        "order_id",
        "product",
        "category",
        "quantity",
        "price",
        "order_date",
    ]

    return df[df[required_columns].isnull().any(axis=1)].copy()


def get_invalid_order_id_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where order_id is missing or invalid."""

    return df[
        df["order_id"].isna()
        | (df["order_id"] <= 0)
    ].copy()


def get_invalid_product_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where product is missing or empty."""

    return df[
        df["product"].isna()
        | df["product"].astype(str).str.strip().eq("")
    ].copy()


def get_invalid_category_value_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where category is missing or empty."""

    return df[
        df["category"].isna()
        | df["category"].astype(str).str.strip().eq("")
    ].copy()


def get_invalid_quantity_value_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where quantity is missing or not a valid integer."""

    numeric_quantity = pd.to_numeric(
        df["quantity"],
        errors="coerce",
    )

    return df[
        numeric_quantity.isna()
        | (numeric_quantity % 1 != 0)
    ].copy()


def get_invalid_price_value_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows where price is missing or not numeric."""

    numeric_price = pd.to_numeric(
        df["price"],
        errors="coerce",
    )

    return df[numeric_price.isna()].copy()


def get_invalid_sales_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows that fail any row-level validation rule."""

    invalid_mask = (
        df["order_id"].isna()
        | (df["order_id"] <= 0)
        | df["order_id"].duplicated(keep=False)
        | df["product"].isna()
        | df["product"].astype(str).str.strip().eq("")
        | df["category"].isna()
        | df["category"].astype(str).str.strip().eq("")
        | df["quantity"].isna()
        | (df["quantity"] <= 0)
        | df["price"].isna()
        | (df["price"] <= 0)
        | df["order_date"].isna()
    )

    parsed_dates = pd.to_datetime(
        df["order_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    invalid_mask = invalid_mask | (
        df["order_date"].notna() & parsed_dates.isna()
    )

    return df[invalid_mask].copy()

def get_sales_rejection_reasons(df: pd.DataFrame) -> pd.Series:
    """Return all rejection reasons for each invalid sales row."""

    reasons = pd.Series("", index=df.index, dtype="object")

    def add_reason(mask: pd.Series, reason: str) -> None:
        for index in df.index[mask]:
            if reasons.loc[index]:
                reasons.loc[index] += f"; {reason}"
            else:
                reasons.loc[index] = reason

    add_reason(
        df["order_id"].isna(),
        "Order ID is missing.",
    )

    add_reason(
        df["order_id"].notna() & (df["order_id"] <= 0),
        "Order ID must be greater than zero.",
    )

    add_reason(
        df["order_id"].duplicated(keep=False),
        "Duplicate order ID.",
    )

    add_reason(
        df["product"].isna()
        | df["product"].astype(str).str.strip().eq(""),
        "Product is missing.",
    )

    add_reason(
        df["category"].isna()
        | df["category"].astype(str).str.strip().eq(""),
        "Category is missing.",
    )

    add_reason(
        df["quantity"].isna(),
        "Quantity is missing.",
    )

    add_reason(
        df["quantity"].notna() & (df["quantity"] <= 0),
        "Quantity must be greater than zero.",
    )

    add_reason(
        df["price"].isna(),
        "Price is missing.",
    )

    add_reason(
        df["price"].notna() & (df["price"] <= 0),
        "Price must be greater than zero.",
    )

    add_reason(
        df["order_date"].isna(),
        "Order date is missing.",
    )

    parsed_dates = pd.to_datetime(
        df["order_date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    add_reason(
        df["order_date"].notna() & parsed_dates.isna(),
        "Invalid order date.",
    )

    return reasons

def split_valid_invalid_sales(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Split sales data into valid and invalid rows."""

    invalid_rows = get_invalid_sales_rows(df)
    invalid_indexes = invalid_rows.index

    valid_rows = df.drop(index=invalid_indexes).copy()
    invalid_rows = df.loc[invalid_indexes].copy()

    reasons = get_sales_rejection_reasons(invalid_rows)

    return valid_rows, invalid_rows, reasons
