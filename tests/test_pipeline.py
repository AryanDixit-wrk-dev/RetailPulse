import pandas as pd

from transformation.sales_transform import transform_sales_data
from pipeline.run_pipeline import run_sales_pipeline


def test_pipeline_succeeds_with_valid_data(tmp_path, monkeypatch):
    csv_file = tmp_path / "valid_sales.csv"

    df = pd.DataFrame(
        {
            "order_id": [1001],
            "product": ["Laptop"],
            "category": ["Electronics"],
            "quantity": [2],
            "price": [55000],
            "order_date": ["2026-09-25"],
        }
    )

    df.to_csv(csv_file, index=False)

    class FakeConnection:
        def close(self):
            pass

    monkeypatch.setattr(
        "pipeline.run_pipeline.get_connection",
        lambda: FakeConnection(),
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_sales_to_database",
        lambda df, conn: len(df),
    )

    reports_generated = False

    def fake_generate_sales_report():
        nonlocal reports_generated
        reports_generated = True

    monkeypatch.setattr(
        "pipeline.run_pipeline.generate_sales_report",
        fake_generate_sales_report,
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is True
    assert reports_generated is True

def test_pipeline_rejects_invalid_data(tmp_path, monkeypatch):
    csv_file = tmp_path / "invalid_sales.csv"

    df = pd.DataFrame(
        {
            "order_id": [1001],
            "product": ["Laptop"],
            "category": ["Electronics"],
            "quantity": [0],
            "price": [55000],
            "order_date": ["2026-09-25"],
        }
    )

    df.to_csv(csv_file, index=False)

    database_called = False

    def fake_get_connection():
        nonlocal database_called
        database_called = True
        return None

    monkeypatch.setattr(
        "pipeline.run_pipeline.get_connection",
        fake_get_connection,
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is False
    assert database_called is False
def test_pipeline_generates_quality_report_for_invalid_data(
    tmp_path,
    monkeypatch,
):
    csv_file = tmp_path / "invalid_sales.csv"

    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 0],
            "price": [55000, 800],
            "order_date": [
                "2026-09-25",
                "2026-09-26",
            ],
        }
    )

    df.to_csv(csv_file, index=False)

    quality_report = {}

    def fake_save_quality_report(report):
        quality_report.update(report)

    monkeypatch.setattr(
        "pipeline.run_pipeline.save_quality_report",
        fake_save_quality_report,
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is False
    assert quality_report["rows_received"] == 2
    assert quality_report["rows_valid"] == 1
    assert quality_report["rows_rejected"] == 1
    assert quality_report["invalid_quantity_rows"] == 1
