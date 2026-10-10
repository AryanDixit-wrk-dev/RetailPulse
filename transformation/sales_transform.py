import pandas as pd


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform sales data for analytics."""

    result = df.copy()
    result["product"] = result["product"].astype(str).str.strip()
    result["category"] = result["category"].astype(str).str.strip()

    result["order_date"] = pd.to_datetime(
        result["order_date"],
        format="%Y-%m-%d",
    )

    result["order_year"] = result["order_date"].dt.year
    result["order_month"] = result["order_date"].dt.month
    result["order_quarter"] = result["order_date"].dt.quarter

    result["unit_price"] = result["price"]

    result["total_sales"] = (
        result["quantity"] * result["price"]
    )

    return result