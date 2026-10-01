import pandas as pd


def calculate_sales_metrics(df: pd.DataFrame) -> dict:
    """Calculate basic sales business metrics."""

    total_orders = int(len(df))
    total_quantity = int(df["quantity"].sum())

    if "total_sales" in df.columns:
        total_sales = float(df["total_sales"].sum())
    else:
        total_sales = float(
            (df["quantity"] * df["price"]).sum()
        )

    average_order_value = (
        total_sales / total_orders
        if total_orders > 0
        else 0.0
    )

    return {
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "total_sales": total_sales,
        "average_order_value": average_order_value,
    }


def sales_by_product(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate sales performance by product."""

    data = df.copy()

    if "total_sales" not in data.columns:
        data["total_sales"] = (
            data["quantity"] * data["price"]
        )

    result = (
        data.groupby("product", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_sales=("total_sales", "sum"),
            total_orders=("order_id", "count"),
        )
        .sort_values("total_sales", ascending=False)
    )

    return result


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate sales performance by category."""

    data = df.copy()

    if "total_sales" not in data.columns:
        data["total_sales"] = (
            data["quantity"] * data["price"]
        )

    result = (
        data.groupby("category", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_sales=("total_sales", "sum"),
            total_orders=("order_id", "count"),
        )
        .sort_values("total_sales", ascending=False)
    )

    return result


def sales_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily sales performance."""

    data = df.copy()

    data["order_date"] = pd.to_datetime(
        data["order_date"]
    )

    if "total_sales" not in data.columns:
        data["total_sales"] = (
            data["quantity"] * data["price"]
        )

    result = (
        data.groupby("order_date", as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            total_sales=("total_sales", "sum"),
            total_orders=("order_id", "count"),
        )
        .sort_values("order_date")
    )

    return result

    return result