import pandas as pd


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform sales data for analytics."""

    result = df.copy()

    result["order_date"] = pd.to_datetime(
        result["order_date"],
        format="%Y-%m-%d",
    )

    result["order_year"] = result["order_date"].dt.year
    result["order_month"] = result["order_date"].dt.month

    result["total_sales"] = (
        result["quantity"] * result["price"]
    )

    return result