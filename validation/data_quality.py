import json
from pathlib import Path

import pandas as pd


def generate_quality_report(df: pd.DataFrame) -> dict:
    """Generate basic data-quality statistics for sales data."""

    rows_received = len(df)

    rows_with_missing_values = df.isnull().any(axis=1)

    invalid_quantity = df["quantity"] <= 0
    invalid_price = df["price"] <= 0

    invalid_order_date = pd.to_datetime(
        df["order_date"],
        format="%Y-%m-%d",
        errors="coerce",
    ).isna()

    invalid_rows = (
        rows_with_missing_values
        | invalid_quantity
        | invalid_price
        | invalid_order_date
    )

    rows_valid = int((~invalid_rows).sum())
    rows_rejected = int(invalid_rows.sum())

    duplicate_order_ids = int(
        df["order_id"].duplicated().sum()
    )

    missing_value_rows = int(
        rows_with_missing_values.sum()
    )

    invalid_quantity_rows = int(
        invalid_quantity.sum()
    )

    invalid_price_rows = int(
        invalid_price.sum()
    )

    invalid_order_date_rows = int(
        invalid_order_date.sum()
    )

    return {
        "rows_received": rows_received,
        "rows_valid": rows_valid,
        "rows_rejected": rows_rejected,
        "duplicate_order_ids": duplicate_order_ids,
        "rows_with_missing_values": missing_value_rows,
        "invalid_quantity_rows": invalid_quantity_rows,
        "invalid_price_rows": invalid_price_rows,
        "invalid_order_date_rows": invalid_order_date_rows,
    }


def save_quality_report(
    report: dict,
    output_path: str = "reports/data_quality_report.json",
):
    """Save the data-quality report as a JSON file."""

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )