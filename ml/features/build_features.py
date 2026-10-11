from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/historical_sales.csv")
OUTPUT_FILE = Path("data/processed/ml_sales_features.csv")


def load_historical_sales() -> pd.DataFrame:
    """Load historical sales data for ML feature generation."""

    df = pd.read_csv(INPUT_FILE)

    df["order_date"] = pd.to_datetime(df["order_date"])

    return df


def load_daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate historical sales to product-day level."""

    daily_sales = (
        df.groupby(
            ["product", "order_date"],
            as_index=False,
        )["quantity"]
        .sum()
        .rename(
            columns={
                "product": "product_name",
                "order_date": "full_date",
            }
        )
    )

    return daily_sales


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build time-series features for product demand forecasting."""

    df = df.copy()

    products = df["product_name"].unique()

    dates = pd.date_range(
        df["full_date"].min(),
        df["full_date"].max(),
        freq="D",
    )

    complete_index = pd.MultiIndex.from_product(
        [products, dates],
        names=["product_name", "full_date"],
    )

    df = (
        df.set_index(["product_name", "full_date"])
        .reindex(complete_index, fill_value=0)
        .reset_index()
    )

    df["quantity"] = df["quantity"].astype(int)

    df["day_of_week"] = df["full_date"].dt.dayofweek
    df["month"] = df["full_date"].dt.month
    df["quarter"] = df["full_date"].dt.quarter
    df["day_of_month"] = df["full_date"].dt.day

    grouped = df.groupby("product_name")["quantity"]

    df["lag_1"] = grouped.shift(1)
    df["lag_7"] = grouped.shift(7)
    df["lag_14"] = grouped.shift(14)

    df["rolling_7"] = (
        grouped.shift(1)
        .rolling(7)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["rolling_14"] = (
        grouped.shift(1)
        .rolling(14)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["rolling_30"] = (
        grouped.shift(1)
        .rolling(30)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["target"] = grouped.shift(-1)

    df = df.dropna().reset_index(drop=True)

    return df


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    historical_sales = load_historical_sales()
    daily_sales = load_daily_sales(historical_sales)
    features = build_features(daily_sales)

    features.to_csv(OUTPUT_FILE, index=False)

    print(f"Feature dataset created: {OUTPUT_FILE}")
    print(f"Rows: {len(features):,}")
    print(f"Columns: {len(features.columns)}")
    print(f"Products: {features['product_name'].nunique()}")
    print(
        f"Date range: "
        f"{features['full_date'].min().date()} "
        f"to "
        f"{features['full_date'].max().date()}"
    )


if __name__ == "__main__":
    main()