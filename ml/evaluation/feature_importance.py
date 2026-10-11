from pathlib import Path

import joblib
import pandas as pd


MODEL_FILE = Path("models/random_forest_sales.joblib")
OUTPUT_FILE = Path("reports/feature_importance.csv")


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


def get_feature_importance(model) -> pd.DataFrame:
    """Return model feature importance in descending order."""

    importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": model.feature_importances_,
        }
    )

    return importance.sort_values(
        "importance",
        ascending=False,
    ).reset_index(drop=True)


def main():
    model = joblib.load(MODEL_FILE)

    importance = get_feature_importance(model)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    importance.to_csv(OUTPUT_FILE, index=False)

    print("Feature importance:")
    print(importance.to_string(index=False))
    print(f"\nReport saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()