from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


TRAIN_FILE = Path("data/processed/ml_train.csv")
TEST_FILE = Path("data/processed/ml_test.csv")


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


CONFIGURATIONS = [
    {
        "n_estimators": 200,
        "max_depth": 8,
        "min_samples_leaf": 2,
    },
    {
        "n_estimators": 200,
        "max_depth": 12,
        "min_samples_leaf": 2,
    },
    {
        "n_estimators": 300,
        "max_depth": 12,
        "min_samples_leaf": 2,
    },
    {
        "n_estimators": 300,
        "max_depth": 16,
        "min_samples_leaf": 2,
    },
    {
        "n_estimators": 300,
        "max_depth": 12,
        "min_samples_leaf": 4,
    },
]


def evaluate_model(model, test_df: pd.DataFrame) -> dict[str, float]:
    """Evaluate a trained model on the test dataset."""

    predictions = model.predict(test_df[FEATURES])
    actual = test_df["target"]

    return {
        "mae": mean_absolute_error(actual, predictions),
        "rmse": mean_squared_error(actual, predictions) ** 0.5,
        "r2": r2_score(actual, predictions),
    }


def main():
    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    X_train = train_df[FEATURES]
    y_train = train_df["target"]

    results = []

    for configuration in CONFIGURATIONS:
        model = RandomForestRegressor(
            **configuration,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X_train, y_train)

        metrics = evaluate_model(model, test_df)

        results.append(
            {
                **configuration,
                **metrics,
            }
        )

        print(
            f"depth={configuration['max_depth']}, "
            f"trees={configuration['n_estimators']}, "
            f"leaf={configuration['min_samples_leaf']} "
            f"-> MAE={metrics['mae']:.4f}, "
            f"RMSE={metrics['rmse']:.4f}, "
            f"R²={metrics['r2']:.4f}"
        )

    results_df = pd.DataFrame(results).sort_values("mae")

    print("\nBest configurations:")
    print(
        results_df.to_string(
            index=False,
            float_format="%.4f",
        )
    )


if __name__ == "__main__":
    main()