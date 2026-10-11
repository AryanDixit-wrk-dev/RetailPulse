from pathlib import Path

import pandas as pd

FEATURE_FILE = Path("data/processed/ml_sales_features.csv")
REPORT_FILE = Path("reports/data_drift_report.csv")

MONITOR_COLUMNS = [
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

LOW_THRESHOLD = 10.0
MODERATE_THRESHOLD = 20.0


def load_features() -> pd.DataFrame:
    """Load the ML feature dataset."""
    df = pd.read_csv(FEATURE_FILE)
    df["full_date"] = pd.to_datetime(df["full_date"])
    return df


def classify_drift(change_pct: float) -> str:
    """Classify drift based on percentage change in the feature mean."""
    absolute_change = abs(change_pct)

    if absolute_change >= MODERATE_THRESHOLD:
        return "HIGH"

    if absolute_change >= LOW_THRESHOLD:
        return "MODERATE"

    return "LOW"


def calculate_drift(
    df: pd.DataFrame,
    reference_days: int = 90,
    current_days: int = 30,
) -> pd.DataFrame:
    """Compare recent feature distributions with a reference period."""
    latest_date = df["full_date"].max()

    reference_start = latest_date - pd.Timedelta(
        days=reference_days + current_days - 1
    )
    current_start = latest_date - pd.Timedelta(
        days=current_days - 1
    )

    reference = df[
        (df["full_date"] >= reference_start)
        & (df["full_date"] < current_start)
    ]

    current = df[df["full_date"] >= current_start]

    results = []

    for column in MONITOR_COLUMNS:
        reference_mean = reference[column].mean()
        current_mean = current[column].mean()

        if reference_mean == 0:
            mean_change_pct = 0.0
        else:
            mean_change_pct = (
                (current_mean - reference_mean)
                / abs(reference_mean)
            ) * 100

        results.append(
            {
                "feature": column,
                "reference_mean": round(reference_mean, 4),
                "current_mean": round(current_mean, 4),
                "mean_change_pct": round(mean_change_pct, 2),
                "status": classify_drift(mean_change_pct),
            }
        )

    return pd.DataFrame(results)


def get_overall_status(report: pd.DataFrame) -> str:
    """Return the overall drift status for the monitored features."""
    if (report["status"] == "HIGH").any():
        return "HIGH"

    if (report["status"] == "MODERATE").any():
        return "MODERATE"

    return "LOW"


def main():
    df = load_features()
    report = calculate_drift(df)

    overall_status = get_overall_status(report)

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT_FILE, index=False)

    print("Data drift report generated successfully.")
    print("Reference period: 90 days")
    print("Current period: 30 days")
    print(f"Overall drift status: {overall_status}")
    print("\nDrift summary:")
    print(report.to_string(index=False))
    print(f"\nReport saved: {REPORT_FILE}")


if __name__ == "__main__":
    main()