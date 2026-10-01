import json

import pandas as pd

from transformation.sales_transform import transform_sales_data
from analytics.generate_report import generate_sales_report


def test_generate_sales_report(tmp_path, monkeypatch):
    sales_df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    class FakeConnection:
        def close(self):
            pass

    monkeypatch.setattr(
        "analytics.generate_report.get_connection",
        lambda: FakeConnection(),
    )

    monkeypatch.setattr(
        "analytics.generate_report.read_sales_from_database",
        lambda conn: sales_df,
    )

    monkeypatch.chdir(tmp_path)
    assert "total_sales" not in sales_df.columns
    generate_sales_report()

    reports_dir = tmp_path / "reports"

    assert (reports_dir / "sales_summary.json").exists()
    assert (reports_dir / "sales_by_product.csv").exists()
    assert (reports_dir / "sales_by_category.csv").exists()
    assert (reports_dir / "sales_by_date.csv").exists()

    summary = json.loads(
        (reports_dir / "sales_summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["total_orders"] == 2
    assert summary["total_quantity"] == 7
    assert summary["total_sales"] == 114000.0
    assert summary["average_order_value"] == 57000.0
def test_generate_sales_report_transforms_data(monkeypatch):
    sales_df = pd.DataFrame(
        {
            "order_id": [1001],
            "product": ["Laptop"],
            "category": ["Electronics"],
            "quantity": [2],
            "price": [55000],
            "order_date": ["2026-09-25"],
        }
    )

    class FakeConnection:
        def close(self):
            pass

    monkeypatch.setattr(
        "analytics.generate_report.get_connection",
        lambda: FakeConnection(),
    )

    monkeypatch.setattr(
        "analytics.generate_report.read_sales_from_database",
        lambda conn: sales_df,
    )

    transformed = False

    def fake_transform(df):
        nonlocal transformed
        transformed = True

        result = df.copy()
        result["total_sales"] = (
            result["quantity"] * result["price"]
        )
        result["order_date"] = pd.to_datetime(
            result["order_date"]
        )
        return result

    monkeypatch.setattr(
        "analytics.generate_report.transform_sales_data",
        fake_transform,
    )

    monkeypatch.chdir(
        __import__("pathlib").Path.cwd()
    )

    generate_sales_report()

    assert transformed is True