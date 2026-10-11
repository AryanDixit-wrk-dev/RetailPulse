from db.analytics import (
    get_sales_by_category,
    get_sales_by_date,
    get_sales_by_product,
    get_sales_summary,
)


def test_get_sales_summary(monkeypatch):
    class FakeCursor:
        description = [
            type("Column", (), {"name": "total_orders"}),
            type("Column", (), {"name": "total_quantity"}),
            type("Column", (), {"name": "total_sales"}),
            type("Column", (), {"name": "average_order_value"}),
        ]

        def execute(self, query):
            assert "COUNT(*)" in query
            assert "SUM(quantity)" in query

        def fetchone(self):
            return (3, 10, 118500, 39500)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    result = get_sales_summary(FakeConnection())

    assert result["total_orders"] == 3
    assert result["total_quantity"] == 10
    assert result["total_sales"] == 118500
    assert result["average_order_value"] == 39500


def test_get_sales_by_product():
    class FakeCursor:
        description = [
            type("Column", (), {"name": "product"}),
            type("Column", (), {"name": "total_quantity"}),
            type("Column", (), {"name": "total_sales"}),
            type("Column", (), {"name": "total_orders"}),
        ]

        def execute(self, query):
            assert "GROUP BY product" in query
            assert "ORDER BY total_sales DESC" in query

        def fetchall(self):
            return [
                ("Laptop", 2, 110000, 1),
                ("Keyboard", 3, 4500, 1),
                ("Mouse", 5, 4000, 1),
            ]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    result = get_sales_by_product(FakeConnection())

    assert list(result["product"]) == [
        "Laptop",
        "Keyboard",
        "Mouse",
    ]

    assert list(result["total_quantity"]) == [2, 3, 5]
    assert list(result["total_sales"]) == [
        110000,
        4500,
        4000,
    ]


def test_get_sales_by_category():
    class FakeCursor:
        description = [
            type("Column", (), {"name": "category"}),
            type("Column", (), {"name": "total_quantity"}),
            type("Column", (), {"name": "total_sales"}),
            type("Column", (), {"name": "total_orders"}),
        ]

        def execute(self, query):
            assert "GROUP BY category" in query
            assert "ORDER BY total_sales DESC" in query

        def fetchall(self):
            return [
                ("Electronics", 2, 110000, 1),
                ("Accessories", 8, 8500, 2),
            ]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    result = get_sales_by_category(FakeConnection())

    assert list(result["category"]) == [
        "Electronics",
        "Accessories",
    ]

    assert list(result["total_quantity"]) == [2, 8]

    assert list(result["total_sales"]) == [
        110000,
        8500,
    ]

    assert list(result["total_orders"]) == [1, 2]


def test_get_sales_by_date():
    class FakeCursor:
        description = [
            type("Column", (), {"name": "order_date"}),
            type("Column", (), {"name": "total_quantity"}),
            type("Column", (), {"name": "total_sales"}),
            type("Column", (), {"name": "total_orders"}),
        ]

        def execute(self, query):
            assert "GROUP BY order_date" in query
            assert "ORDER BY order_date" in query

        def fetchall(self):
            return [
                ("2026-09-25", 2, 110000, 1),
                ("2026-09-26", 5, 4000, 1),
                ("2026-09-27", 3, 4500, 1),
            ]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    result = get_sales_by_date(FakeConnection())

    assert list(result["order_date"]) == [
        "2026-09-25",
        "2026-09-26",
        "2026-09-27",
    ]

    assert list(result["total_quantity"]) == [2, 5, 3]

    assert list(result["total_sales"]) == [
        110000,
        4000,
        4500,
    ]

    assert list(result["total_orders"]) == [1, 1, 1]