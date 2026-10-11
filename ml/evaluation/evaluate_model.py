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


def evaluate_model(
    model,
    df: pd.DataFrame,
) -> dict[str, float]:
    """Evaluate the trained forecasting model."""

    X = df[FEATURES]
    actual = df["target"]

    predictions = model.predict(X)

    mae = mean_absolute_error(actual, predictions)
    rmse = mean_squared_error(actual, predictions) ** 0.5
    r2 = r2_score(actual, predictions)

    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


def main():
    df = pd.read_csv(TEST_FILE)
    model = joblib.load(MODEL_FILE)

    metrics = evaluate_model(model, df)

    print("Random Forest evaluation")
    print(f"MAE:  {metrics['mae']:.4f}")
    print(f"RMSE: {metrics['rmse']:.4f}")
    print(f"R²:   {metrics['r2']:.4f}")


if __name__ == "__main__":
    main()