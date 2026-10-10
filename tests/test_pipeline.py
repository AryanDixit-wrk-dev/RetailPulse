import pandas as pd

from pipeline.run_pipeline import run_sales_pipeline


def mock_pipeline_tracking(monkeypatch):
    monkeypatch.setattr(
        "pipeline.run_pipeline.pipeline_run_exists",
        lambda conn, pipeline_name, source_hash: False,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.create_pipeline_run",
        lambda conn, pipeline_name, source_file, source_hash: 1,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.complete_pipeline_run",
        lambda conn, run_id, status, records_processed=None, error_message=None: None,
    )


def mock_database_loaders(monkeypatch):
    monkeypatch.setattr(
        "pipeline.run_pipeline.load_sales_to_database",
        lambda df, conn, pipeline_run_id: len(df),
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_warehouse_data",
        lambda df, conn, pipeline_run_id: len(df),
    )


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

    mock_pipeline_tracking(monkeypatch)
    mock_database_loaders(monkeypatch)

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

    class FakeConnection:
        def close(self):
            pass

    database_called = False

    def fake_load_sales_to_database(df, conn, pipeline_run_id):
        nonlocal database_called
        database_called = True
        return len(df)

    def fake_load_quarantine_records(
        df,
        conn,
        pipeline_run_id,
        source_file,
        rejection_reason,
    ):
        return len(df)

    monkeypatch.setattr(
        "pipeline.run_pipeline.get_connection",
        lambda: FakeConnection(),
    )

    mock_pipeline_tracking(monkeypatch)

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_sales_to_database",
        fake_load_sales_to_database,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_warehouse_data",
        lambda df, conn, pipeline_run_id: len(df),
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_quarantine_records",
        fake_load_quarantine_records,
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is True
    assert database_called is True


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

    class FakeConnection:
        def close(self):
            pass

    quality_report = {}

    def fake_save_quality_report(report):
        quality_report.update(report)

    def fake_load_quarantine_records(
        df,
        conn,
        pipeline_run_id,
        source_file,
        rejection_reason,
    ):
        return len(df)

    def fake_load_sales_to_database(
        df,
        conn,
        pipeline_run_id,
    ):
        return len(df)

    monkeypatch.setattr(
        "pipeline.run_pipeline.get_connection",
        lambda: FakeConnection(),
    )

    mock_pipeline_tracking(monkeypatch)

    monkeypatch.setattr(
        "pipeline.run_pipeline.save_quality_report",
        fake_save_quality_report,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_quarantine_records",
        fake_load_quarantine_records,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_sales_to_database",
        fake_load_sales_to_database,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_warehouse_data",
        lambda df, conn, pipeline_run_id: len(df),
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is True
    assert quality_report["rows_received"] == 2
    assert quality_report["rows_valid"] == 1
    assert quality_report["rows_rejected"] == 1
    assert quality_report["invalid_quantity_rows"] == 1


def test_pipeline_skips_already_processed_batch(tmp_path, monkeypatch):
    csv_file = tmp_path / "sales.csv"

    csv_file.write_text(
        """order_id,product,category,quantity,price,order_date
1001,Laptop,Electronics,2,55000,2026-10-02
""",
        encoding="utf-8",
    )

    class FakeConnection:
        def close(self):
            pass

    database_called = False

    def fake_load_sales_to_database(df, conn, pipeline_run_id):
        nonlocal database_called
        database_called = True
        return len(df)

    monkeypatch.setattr(
        "pipeline.run_pipeline.get_connection",
        lambda: FakeConnection(),
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.pipeline_run_exists",
        lambda conn, pipeline_name, source_hash: True,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_sales_to_database",
        fake_load_sales_to_database,
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is True
    assert database_called is False


def test_pipeline_quarantines_invalid_quantity_rows(
    tmp_path,
    monkeypatch,
):
    csv_file = tmp_path / "sales.csv"

    df = pd.DataFrame(
        {
            "order_id": [2001, 2002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 0],
            "price": [55000, 800],
            "order_date": [
                "2026-10-10",
                "2026-10-10",
            ],
        }
    )

    df.to_csv(csv_file, index=False)

    class FakeConnection:
        def close(self):
            pass

    loaded_sales = []
    quarantined_rows = []

    def fake_load_sales_to_database(
        df,
        conn,
        pipeline_run_id,
    ):
        loaded_sales.extend(df["order_id"].tolist())
        return len(df)

    def fake_load_quarantine_records(
        df,
        conn,
        pipeline_run_id,
        source_file,
        rejection_reason,
    ):
        quarantined_rows.append(
            {
                "order_ids": df["order_id"].tolist(),
                "reason": rejection_reason,
            }
        )
        return len(df)

    monkeypatch.setattr(
        "pipeline.run_pipeline.get_connection",
        lambda: FakeConnection(),
    )

    mock_pipeline_tracking(monkeypatch)

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_sales_to_database",
        fake_load_sales_to_database,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_warehouse_data",
        lambda df, conn, pipeline_run_id: len(df),
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.load_quarantine_records",
        fake_load_quarantine_records,
    )

    monkeypatch.setattr(
        "pipeline.run_pipeline.generate_sales_report",
        lambda: None,
    )

    result = run_sales_pipeline(str(csv_file))

    assert result is True
    assert loaded_sales == [2001]
    assert quarantined_rows == [
        {
            "order_ids": [2002],
            "reason": "Quantity must be greater than zero.",
        }
    ]