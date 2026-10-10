import pandas as pd

from db.loaders.warehouse_loader import load_warehouse_data


def test_load_warehouse_data():
    df = pd.DataFrame(
        [
            {
                "order_id": 9001,
                "product": "Laptop",
                "category": "Electronics",
                "quantity": 2,
                "price": 55000.00,
                "order_date": pd.Timestamp("2026-10-11"),
            }
        ]
    )

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, *args, **kwargs):
            pass

        def fetchone(self):
            return (1,)

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    result = load_warehouse_data(
        df,
        FakeConnection(),
        pipeline_run_id=174,
    )

    assert result == 1
