from fastapi import APIRouter, Depends

from api.auth import verify_api_key
from api.dependencies import get_db_connection
from api.models.sales import (
    SalesByCategory,
    SalesByDate,
    SalesByProduct,
    SalesSummary,
)


router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
    dependencies=[Depends(verify_api_key)],
)


def get_sales_data(
    table_name: str,
    conn,
) -> list[dict]:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [column.name for column in cursor.description]
        rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


@router.get("/summary", response_model=SalesSummary)
def sales_summary(conn=Depends(get_db_connection)):
    try:
        return get_sales_data("sales_summary", conn)[0]
    finally:
        conn.close()


@router.get("/by-product", response_model=list[SalesByProduct])
def sales_by_product(conn=Depends(get_db_connection)):
    try:
        return get_sales_data("sales_by_product", conn)
    finally:
        conn.close()


@router.get("/by-category", response_model=list[SalesByCategory])
def sales_by_category(conn=Depends(get_db_connection)):
    try:
        return get_sales_data("sales_by_category", conn)
    finally:
        conn.close()


@router.get("/by-date", response_model=list[SalesByDate])
def sales_by_date(conn=Depends(get_db_connection)):
    try:
        return get_sales_data("sales_by_date", conn)
    finally:
        conn.close()