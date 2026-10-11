from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml.features.build_features import (
    build_features,
    load_daily_sales,
    load_historical_sales,
)
from ml.training.split_data import split_data


FEATURE_FILE = Path("data/processed/ml_sales_features.csv")
CURRENT_MODEL_FILE = Path("models/random_forest_sales.joblib")
CANDIDATE_MODEL_FILE = Path("models/random_forest_sales_candidate.joblib")
REPORT_FILE = Path("reports/retraining_evaluation.csv")


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
    """Train a Random Forest candidate model."""

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        df[FEATURES],
        df["target"],
    )

    return model


def evaluate_model(
    model,
    df: pd.DataFrame,
) -> dict[str, float]:
    """Evaluate a model on a test dataset."""

    predictions = model.predict(df[FEATURES])
    actual = df["target"]

    return {
        "mae": mean_absolute_error(actual, predictions),
        "rmse": mean_squared_error(actual, predictions) ** 0.5,
        "r2": r2_score(actual, predictions),
    }


def rebuild_features() -> pd.DataFrame:
    """Rebuild the ML feature dataset from historical sales."""

    historical_sales = load_historical_sales()
    daily_sales = load_daily_sales(historical_sales)
    features = build_features(daily_sales)

    features.to_csv(
        FEATURE_FILE,
        index=False,
    )

    return features


def compare_models(
    current_metrics: dict[str, float],
    candidate_metrics: dict[str, float],
) -> str:
    """Compare candidate and current model performance."""

    if candidate_metrics["mae"] < current_metrics["mae"]:
        return "IMPROVED"

    if candidate_metrics["mae"] > current_metrics["mae"]:
        return "WORSE"

    return "UNCHANGED"


def main():
    print("Starting model retraining workflow...")

    features = rebuild_features()

    train, test = split_data(features)

    print(f"Feature rows: {len(features):,}")
    print(f"Training rows: {len(train):,}")
    print(f"Test rows: {len(test):,}")

    current_model = joblib.load(
        CURRENT_MODEL_FILE
    )

    candidate_model = train_model(train)

    current_metrics = evaluate_model(
        current_model,
        test,
    )

    candidate_metrics = evaluate_model(
        candidate_model,
        test,
    )

    comparison = compare_models(
        current_metrics,
        candidate_metrics,
    )

    print("\nCurrent model")
    print(f"MAE:  {current_metrics['mae']:.4f}")
    print(f"RMSE: {current_metrics['rmse']:.4f}")
    print(f"R2:   {current_metrics['r2']:.4f}")

    print("\nCandidate model")
    print(f"MAE:  {candidate_metrics['mae']:.4f}")
    print(f"RMSE: {candidate_metrics['rmse']:.4f}")
    print(f"R2:   {candidate_metrics['r2']:.4f}")

    print(f"\nComparison: {comparison}")

    CANDIDATE_MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        candidate_model,
        CANDIDATE_MODEL_FILE,
    )

    report = pd.DataFrame(
        [
            {
                "model": "current",
                **current_metrics,
            },
            {
                "model": "candidate",
                **candidate_metrics,
            },
        ]
    )

    report["comparison"] = comparison

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report.to_csv(
        REPORT_FILE,
        index=False,
    )

    print(
        f"\nCandidate model saved: "
        f"{CANDIDATE_MODEL_FILE}"
    )
    print(
        f"Evaluation report saved: "
        f"{REPORT_FILE}"
    )


if __name__ == "__main__":
    main()