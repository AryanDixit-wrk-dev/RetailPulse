import pandas as pd

from transformation.sales_transform import transform_sales_data


def test_transform_sales_data_adds_total_sales():
    df = pd.DataFrame(
        {
            "order_id": [1001, 1002],
            "product": ["Laptop", "Mouse"],
            "category": ["Electronics", "Accessories"],
            "quantity": [2, 5],
            "price": [55000, 800],
            "order_date": [
                "2026-09-25",
                "2026-09-26",
            ],
        }
    )

    result = transform_sales_data(df)

    assert "total_sales" in result.columns
    assert result.loc[0, "total_sales"] == 110000
    assert result.loc[1, "total_sales"] == 4000

def test_transform_sales_data_converts_order_date():
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

    result = transform_sales_data(df)

    assert pd.api.types.is_datetime64_any_dtype(
        result["order_date"]
    )
def test_transform_sales_data_adds_date_parts():
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

    result = transform_sales_data(df)

    assert result.loc[0, "order_year"] == 2026
    assert result.loc[0, "order_month"] == 9