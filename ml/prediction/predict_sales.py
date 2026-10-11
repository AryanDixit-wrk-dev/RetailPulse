from pathlib import Path

import joblib
import pandas as pd


FEATURE_FILE = Path("data/processed/ml_sales_features.csv")
MODEL_FILE = Path("models/random_forest_sales.joblib")
OUTPUT_FILE = Path("reports/sales_predictions.csv")


FEATURES = [
    "day_of_week",
    "month",
    "quarter",
    "day_of_month",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_7",
    "rolling_14",
    "rolling_30",
]


def load_model():
    """Load the trained forecasting model."""

    return joblib.load(MODEL_FILE)


def create_predictions(
    model,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Generate next-day demand predictions."""

    df = df.copy()
    df["full_date"] = pd.to_datetime(df["full_date"])

    latest_date = df["full_date"].max()

    latest_features = df[
        df["full_date"] == latest_date
    ].copy()

    predictions = latest_features[
        ["product_name", "full_date"]
    ]

    predictions["forecast_date"] = (
        latest_date + pd.Timedelta(days=1)
    )

    predictions["predicted_quantity"] = model.predict(
        latest_features[FEATURES]
    )

    predictions["predicted_quantity"] = (
        predictions["predicted_quantity"]
        .clip(lower=0)
        .round(2)
    )

    return predictions[
        [
            "forecast_date",
            "product_name",
            "predicted_quantity",
        ]
    ]


def main():
    df = pd.read_csv(FEATURE_FILE)

    model = load_model()

    predictions = create_predictions(model, df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    predictions.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    latest_date = predictions["forecast_date"].max()

    latest_predictions = predictions[
        predictions["forecast_date"] == latest_date
    ].sort_values(
        "predicted_quantity",
        ascending=False,
    )

    print("Sales predictions generated successfully.")
    print(f"Forecast date: {latest_date.date()}")
    print("\nNext-day demand predictions:")
    print(
        latest_predictions.to_string(
            index=False
        )
    )
    print(f"\nReport saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()