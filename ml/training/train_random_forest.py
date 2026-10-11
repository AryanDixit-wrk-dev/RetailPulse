from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


TRAIN_FILE = Path("data/processed/ml_train.csv")
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


def train_model(df: pd.DataFrame) -> RandomForestRegressor:
    """Train the Random Forest demand forecasting model."""

    X = df[FEATURES]
    y = df["target"]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X, y)

    return model


def main():
    df = pd.read_csv(TRAIN_FILE)

    model = train_model(df)

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_FILE)

    print("Random Forest model trained successfully.")
    print(f"Training rows: {len(df):,}")
    print(f"Features: {len(FEATURES)}")
    print("n_estimators: 200")
    print("max_depth: 8")
    print("min_samples_leaf: 2")
    print(f"Model saved: {MODEL_FILE}")


if __name__ == "__main__":
    main()