from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


TEST_FILE = Path("data/processed/ml_test.csv")


def evaluate_baseline(df: pd.DataFrame) -> dict[str, float]:
    """Evaluate a 7-day seasonal naive forecast."""

    actual = df["target"]
    predictions = df["lag_7"]

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

    metrics = evaluate_baseline(df)

    print("Baseline model: 7-day seasonal naive")
    print(f"MAE:  {metrics['mae']:.4f}")
    print(f"RMSE: {metrics['rmse']:.4f}")
    print(f"R²:   {metrics['r2']:.4f}")


if __name__ == "__main__":
    main()