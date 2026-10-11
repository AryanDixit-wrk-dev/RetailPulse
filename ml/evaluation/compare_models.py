from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


TEST_FILE = Path("data/processed/ml_test.csv")
MODEL_FILE = Path("models/random_forest_sales.joblib")


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


def calculate_metrics(actual, predictions) -> dict[str, float]:
    """Calculate forecasting evaluation metrics."""

    return {
        "mae": mean_absolute_error(actual, predictions),
        "rmse": mean_squared_error(actual, predictions) ** 0.5,
        "r2": r2_score(actual, predictions),
    }


def main():
    df = pd.read_csv(TEST_FILE)

    actual = df["target"]

    predictions = {
        "1-day lag": df["lag_1"],
        "7-day lag": df["lag_7"],
        "7-day rolling": df["rolling_7"],
    }

    model = joblib.load(MODEL_FILE)
    predictions["Random Forest"] = model.predict(df[FEATURES])

    results = []

    for name, prediction in predictions.items():
        metrics = calculate_metrics(actual, prediction)

        results.append(
            {
                "model": name,
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "r2": metrics["r2"],
            }
        )

    results_df = pd.DataFrame(results).sort_values("mae")

    print("Model comparison")
    print(results_df.to_string(index=False, float_format="%.4f"))


if __name__ == "__main__":
    main()