from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_FILE = Path("data/raw/historical_sales.csv")

PRODUCTS = [
    ("Laptop", "Electronics", 55000, 5.0),
    ("Monitor", "Electronics", 18000, 8.0),
    ("Keyboard", "Accessories", 2500, 12.0),
    ("Mouse", "Accessories", 800, 15.0),
    ("Headphones", "Accessories", 3500, 10.0),
    ("Webcam", "Electronics", 4500, 7.0),
    ("Tablet", "Electronics", 28000, 6.0),
    ("USB Hub", "Accessories", 1200, 13.0),
]


def generate_sales(
    start_date: str = "2025-01-01",
    end_date: str = "2026-10-09",
) -> pd.DataFrame:
    """Generate historical sales with trend, seasonality, and noise."""

    rng = np.random.default_rng(42)

    dates = pd.date_range(start_date, end_date, freq="D")

    rows = []
    order_id = 200000

    for date in dates:
        days_from_start = (date - dates[0]).days

        trend = 1 + (days_from_start / len(dates)) * 0.25

        weekly_factor = {
            0: 0.90,
            1: 0.95,
            2: 1.00,
            3: 1.05,
            4: 1.15,
            5: 1.30,
            6: 1.20,
        }[date.dayofweek]

        seasonal_factor = 1.0

        if date.month in [10, 11, 12]:
            seasonal_factor = 1.30
        elif date.month in [6, 7]:
            seasonal_factor = 0.90

        for product, category, price, base_demand in PRODUCTS:
            demand = (
                base_demand
                * trend
                * weekly_factor
                * seasonal_factor
            )

            quantity = max(
                1,
                int(round(rng.normal(demand, demand * 0.20))),
            )

            actual_price = round(
                price * rng.normal(1.0, 0.03),
                2,
            )

            rows.append(
                {
                    "order_id": order_id,
                    "product": product,
                    "category": category,
                    "quantity": quantity,
                    "price": actual_price,
                    "order_date": date,
                }
            )

            order_id += 1

    return pd.DataFrame(rows)


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    sales = generate_sales()

    sales.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated {len(sales):,} sales records.")
    print(
        f"Date range: "
        f"{sales['order_date'].min().date()} "
        f"to "
        f"{sales['order_date'].max().date()}"
    )
    print(f"Products: {sales['product'].nunique()}")
    print(f"Categories: {sales['category'].nunique()}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()