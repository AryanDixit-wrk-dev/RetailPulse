from pathlib import Path

import joblib
import pandas as pd


TEST_FILE = Path("data/processed/ml_test.csv")
MODEL_FILE = Path("models/random_forest_sales.joblib")
REPORT_FILE = Path("reports/model_performance_monitoring.csv")


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


def create_diagnostics(
    model,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create prediction and error diagnostics."""

    diagnostics = df[
        ["product_name", "full_date", "target"]
    ].copy()

    diagnostics["full_date"] = pd.to_datetime(
        diagnostics["full_date"]
    )

    diagnostics["predicted"] = model.predict(df[FEATURES])

    diagnostics["error"] = (
        diagnostics["target"] - diagnostics["predicted"]
    )

    diagnostics["absolute_error"] = diagnostics["error"].abs()

    diagnostics["month"] = diagnostics["full_date"].dt.month

    return diagnostics


def print_product_metrics(df: pd.DataFrame):
    """Print prediction error by product."""

    result = (
        df.groupby("product_name")
        .agg(
            actual_mean=("target", "mean"),
            predicted_mean=("predicted", "mean"),
            mae=("absolute_error", "mean"),
        )
        .sort_values("mae")
    )

    print("\nMAE by product")
    print(result.to_string(float_format="%.4f"))


def print_month_metrics(df: pd.DataFrame):
    """Print prediction error by month."""

    result = (
        df.groupby("month")
        .agg(
            actual_mean=("target", "mean"),
            predicted_mean=("predicted", "mean"),
            mae=("absolute_error", "mean"),
        )
        .sort_values("month")
    )

    print("\nMAE by month")
    print(result.to_string(float_format="%.4f"))


def create_time_metrics(
    df: pd.DataFrame,
    window_days: int = 30,
) -> pd.DataFrame:
    """Calculate model performance over consecutive time windows."""

    latest_date = df["full_date"].max()
    earliest_date = df["full_date"].min()

    results = []
    window_end = latest_date

    while window_end >= earliest_date:
        window_start = window_end - pd.Timedelta(days=window_days - 1)

        window = df[
            (df["full_date"] >= window_start)
            & (df["full_date"] <= window_end)
        ]

        if window.empty:
            break

        results.append(
            {
                "window_start": window_start.date(),
                "window_end": window_end.date(),
                "rows": len(window),
                "mae": round(window["absolute_error"].mean(), 4),
                "rmse": round(
                    (window["error"] ** 2).mean() ** 0.5,
                    4,
                ),
                "actual_mean": round(window["target"].mean(), 4),
                "predicted_mean": round(
                    window["predicted"].mean(),
                    4,
                ),
            }
        )

        window_end = window_start - pd.Timedelta(days=1)

    return pd.DataFrame(results)


def get_performance_status(
    recent_mae: float,
    overall_mae: float,
) -> str:
    """Classify recent model performance against overall performance."""

    if overall_mae == 0:
        return "UNKNOWN"

    change_pct = (
        (recent_mae - overall_mae)
        / overall_mae
    ) * 100

    if change_pct >= 30:
        return "HIGH"

    if change_pct >= 15:
        return "MODERATE"

    return "LOW"


def print_performance_monitoring(
    df: pd.DataFrame,
):
    """Print recent and historical model performance."""

    overall_mae = df["absolute_error"].mean()
    overall_rmse = (
        (df["error"] ** 2).mean()
        ** 0.5
    )

    time_metrics = create_time_metrics(df)

    recent_mae = time_metrics.iloc[0]["mae"]
    status = get_performance_status(
        recent_mae,
        overall_mae,
    )

    print("\nModel performance monitoring")
    print(f"Overall MAE: {overall_mae:.4f}")
    print(f"Overall RMSE: {overall_rmse:.4f}")
    print(f"Recent {30}-day MAE: {recent_mae:.4f}")
    print(f"Performance status: {status}")

    print("\nPerformance by time window")
    print(
        time_metrics.head(6).to_string(
            index=False
        )
    )

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    time_metrics.to_csv(
        REPORT_FILE,
        index=False,
    )

    print(f"\nMonitoring report saved: {REPORT_FILE}")


def print_largest_errors(
    df: pd.DataFrame,
    count: int = 10,
):
    """Print predictions with the largest absolute errors."""

    result = (
        df.sort_values(
            "absolute_error",
            ascending=False,
        )
        .head(count)
    )

    print(f"\nLargest {count} prediction errors")
    print(
        result[
            [
                "product_name",
                "full_date",
                "target",
                "predicted",
                "error",
                "absolute_error",
            ]
        ].to_string(
            index=False,
            float_format="%.4f",
        )
    )


def main():
    test_df = pd.read_csv(TEST_FILE)
    model = joblib.load(MODEL_FILE)

    diagnostics = create_diagnostics(
        model,
        test_df,
    )

    print_product_metrics(diagnostics)
    print_month_metrics(diagnostics)
    print_performance_monitoring(diagnostics)
    print_largest_errors(diagnostics)


if __name__ == "__main__":
    main()