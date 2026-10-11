from datetime import date

from fastapi import APIRouter, Depends, Query

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
)


def build_sales_conditions(
    start_date: date | None,
    end_date: date | None,
    products: list[str] | None,
    categories: list[str] | None,
):
    conditions = []
    parameters = []

    if start_date is not None:
        conditions.append("d.full_date >= %s")
        parameters.append(start_date)

    if end_date is not None:
        conditions.append("d.full_date <= %s")
        parameters.append(end_date)

    if products:
        conditions.append("p.product_name = ANY(%s)")
        parameters.append(products)

    if categories:
        conditions.append("c.category_name = ANY(%s)")
        parameters.append(categories)

    return conditions, parameters


def get_sales_summary(
    conn,
    start_date: date | None = None,
    end_date: date | None = None,
    products: list[str] | None = None,
    categories: list[str] | None = None,
) -> dict:
    query = """
        SELECT
            COALESCE(SUM(f.total_sales), 0) AS total_sales,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COALESCE(SUM(f.quantity), 0) AS total_quantity
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        JOIN dim_product p
            ON f.product_key = p.product_key
        JOIN dim_category c
            ON f.category_key = c.category_key
    """

    conditions, parameters = build_sales_conditions(
        start_date,
        end_date,
        products,
        categories,
    )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    with conn.cursor() as cursor:
        cursor.execute(query, parameters)
        columns = [column.name for column in cursor.description]
        row = cursor.fetchone()

    return dict(zip(columns, row))


def get_product_sales(
    conn,
    start_date: date | None = None,
    end_date: date | None = None,
    products: list[str] | None = None,
    categories: list[str] | None = None,
) -> list[dict]:
    query = """
        SELECT
            p.product_name,
            SUM(f.quantity) AS total_quantity,
            SUM(f.total_sales) AS total_sales
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        JOIN dim_category c
            ON f.category_key = c.category_key
        JOIN dim_date d
            ON f.date_key = d.date_key
    """

    conditions, parameters = build_sales_conditions(
        start_date,
        end_date,
        products,
        categories,
    )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY p.product_name
        ORDER BY total_sales DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, parameters)
        columns = [column.name for column in cursor.description]
        rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def get_category_sales(
    conn,
    start_date: date | None = None,
    end_date: date | None = None,
    products: list[str] | None = None,
    categories: list[str] | None = None,
) -> list[dict]:
    query = """
        SELECT
            c.category_name,
            SUM(f.quantity) AS total_quantity,
            SUM(f.total_sales) AS total_sales
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        JOIN dim_category c
            ON f.category_key = c.category_key
        JOIN dim_date d
            ON f.date_key = d.date_key
    """

    conditions, parameters = build_sales_conditions(
        start_date,
        end_date,
        products,
        categories,
    )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY c.category_name
        ORDER BY total_sales DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, parameters)
        columns = [column.name for column in cursor.description]
        rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def get_date_sales(
    conn,
    start_date: date | None = None,
    end_date: date | None = None,
    products: list[str] | None = None,
    categories: list[str] | None = None,
) -> list[dict]:
    query = """
        SELECT
            d.date_key,
            SUM(f.quantity) AS total_quantity,
            SUM(f.total_sales) AS total_sales,
            COUNT(DISTINCT f.order_id) AS total_orders
        FROM fact_sales f
        JOIN dim_product p
            ON f.product_key = p.product_key
        JOIN dim_category c
            ON f.category_key = c.category_key
        JOIN dim_date d
            ON f.date_key = d.date_key
    """

    conditions, parameters = build_sales_conditions(
        start_date,
        end_date,
        products,
        categories,
    )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY d.date_key
        ORDER BY d.date_key
    """

    with conn.cursor() as cursor:
        cursor.execute(query, parameters)
        columns = [column.name for column in cursor.description]
        rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


@router.get("/summary", response_model=SalesSummary)
def sales_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    products: list[str] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    conn=Depends(get_db_connection),
):
    try:
        return get_sales_summary(
            conn,
            start_date=start_date,
            end_date=end_date,
            products=products,
            categories=categories,
        )
    finally:
        conn.close()


@router.get("/by-product", response_model=list[SalesByProduct])
def sales_by_product(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    products: list[str] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    conn=Depends(get_db_connection),
):
    try:
        return get_product_sales(
            conn,
            start_date=start_date,
            end_date=end_date,
            products=products,
            categories=categories,
        )
    finally:
        conn.close()


@router.get("/by-category", response_model=list[SalesByCategory])
def sales_by_category(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    products: list[str] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    conn=Depends(get_db_connection),
):
    try:
        return get_category_sales(
            conn,
            start_date=start_date,
            end_date=end_date,
            products=products,
            categories=categories,
        )
    finally:
        conn.close()


@router.get("/by-date", response_model=list[SalesByDate])
def sales_by_date(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    products: list[str] | None = Query(default=None),
    categories: list[str] | None = Query(default=None),
    conn=Depends(get_db_connection),
):
    try:
        return get_date_sales(
            conn,
            start_date=start_date,
            end_date=end_date,
            products=products,
            categories=categories,
        )
    finally:
        conn.close()