import json
import pandas as pd


from validation.data_quality import generate_quality_report


def test_quality_report_for_valid_data():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    report = generate_quality_report(df)

    assert report["rows_received"] == 2
    assert report["rows_valid"] == 2
    assert report["rows_rejected"] == 0

def test_quality_report_detects_duplicate_orders():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1001, 1002],
            "product": ["Laptop", "Laptop", "Mouse"],
            "category": ["Electronics", "Electronics", "Accessories"],
            "quantity": [2, 2, 5],
            "price": [55000, 55000, 800],
            "order_date": [
                "2026-09-25",
                "2026-09-25",
                "2026-09-26",
            ],
        }
    )

    report = generate_quality_report(df)

    assert report["rows_received"] == 3
    assert report["duplicate_order_ids"] == 1
def test_quality_report_detects_missing_values():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", None, "Mouse"],
            "category": ["Electronics", "Accessories", "Accessories"],
            "quantity": [2, 5, 3],
            "price": [55000, 800, 1500],
            "order_date": [
                "2026-09-25",
                "2026-09-26",
                "2026-09-27",
            ],
        }
    )

    report = generate_quality_report(df)

    assert report["rows_received"] == 3
    assert report["rows_with_missing_values"] == 1
def test_quality_report_detects_invalid_quantity():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "category": [
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            "quantity": [2, 0, -1],
            "price": [55000, 800, 1500],
            "order_date": [
                "2026-09-25",
                "2026-09-26",
                "2026-09-27",
            ],
        }
    )

    report = generate_quality_report(df)

    assert report["invalid_quantity_rows"] == 2
def test_quality_report_detects_invalid_price():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "category": [
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            "quantity": [2, 5, 3],
            "price": [55000, 0, -1500],
            "order_date": [
                "2026-09-25",
                "2026-09-26",
                "2026-09-27",
            ],
        }
    )

    report = generate_quality_report(df)

    assert report["invalid_price_rows"] == 2
def test_quality_report_detects_invalid_order_date():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "category": [
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            "quantity": [2, 5, 3],
            "price": [55000, 800, 1500],
            "order_date": [
                "2026-09-25",
                "not-a-date",
                "2026-09-27",
            ],
        }
    )

    report = generate_quality_report(df)

    assert report["invalid_order_date_rows"] == 1
def test_quality_report_contains_all_metrics():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": ["2026-09-25", "2026-09-26"],
        }
    )

    report = generate_quality_report(df)

    expected_keys = {
        "rows_received",
        "rows_valid",
        "rows_rejected",
        "duplicate_order_ids",
        "rows_with_missing_values",
        "invalid_quantity_rows",
        "invalid_price_rows",
        "invalid_order_date_rows",
    }

    assert set(report.keys()) == expected_keys
def test_save_quality_report(tmp_path):
    from validation.data_quality import save_quality_report

    report = {
        "rows_received": 10,
        "rows_valid": 8,
        "rows_rejected": 2,
    }

    output_path = tmp_path / "data_quality_report.json"

    save_quality_report(report, str(output_path))

    assert output_path.exists()

    saved_report = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved_report == report
def test_quality_report_marks_invalid_rows_as_rejected():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "category": [
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            "quantity": [2, 0, 3],
            "price": [55000, 800, 1500],
            "order_date": [
                "2026-09-25",
                "2026-09-26",
                "2026-09-27",
            ],
        }
    )

    report = generate_quality_report(df)

    assert report["rows_received"] == 3
    assert report["rows_valid"] == 2
    assert report["rows_rejected"] == 1
