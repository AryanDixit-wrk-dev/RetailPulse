from pathlib import Path

import pandas as pd


PREDICTION_FILE = Path("reports/sales_predictions.csv")
HISTORICAL_FILE = Path("data/raw/historical_sales.csv")


def main():
    predictions = pd.read_csv(PREDICTION_FILE)
    historical = pd.read_csv(HISTORICAL_FILE)

    historical["order_date"] = pd.to_datetime(
        historical["order_date"]
    )

    actual = (
        historical[
            historical["order_date"] == "2026-10-09"
        ]
        .groupby("product")["quantity"]
        .sum()
        .reset_index()
    )

    actual = actual.rename(
        columns={
            "product": "product_name",
            "quantity": "actual_quantity",
        }
    )

    forecast = predictions[
        predictions["full_date"] == "2026-10-08"
    ]

    result = forecast.merge(
        actual,
        on="product_name",
    )

    result["error"] = (
        result["actual_quantity"]
        - result["predicted_quantity"]
    )

    result["absolute_error"] = result["error"].abs()

    print("Forecast vs actual for 2026-10-09")
    print(
        result.sort_values(
            "absolute_error",
            ascending=False,
        ).to_string(index=False)
    )

    mae = result["absolute_error"].mean()

    print(f"\nMAE: {mae:.4f}")


if __name__ == "__main__":
    main()