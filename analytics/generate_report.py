import json
from pathlib import Path

from db.connection import get_connection
from db.readers.sales_reader import read_sales_from_database
from analytics.sales_metrics import (
    calculate_sales_metrics,
    sales_by_product,
    sales_by_category,
    sales_by_date,
)


def generate_sales_report():
    """Generate sales summary, product, category, and date reports."""

    conn = get_connection()
    try:
        sales_df = read_sales_from_database(conn)
    finally:
        conn.close()

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    metrics = calculate_sales_metrics(sales_df)

    summary_path = reports_dir / "sales_summary.json"
    summary_path.write_text(
        json.dumps(metrics, indent=4),
        encoding="utf-8",
    )

    product_report = sales_by_product(sales_df)
    product_path = reports_dir / "sales_by_product.csv"
    product_report.to_csv(product_path, index=False)

    category_report = sales_by_category(sales_df)
    category_path = reports_dir / "sales_by_category.csv"
    category_report.to_csv(category_path, index=False)

    date_report = sales_by_date(sales_df)
    date_path = reports_dir / "sales_by_date.csv"
    date_report.to_csv(date_path, index=False)

    print(f"Summary report generated: {summary_path}")
    print(f"Product report generated: {product_path}")
    print(f"Category report generated: {category_path}")
    print(f"Date report generated: {date_path}")


if __name__ == "__main__":
    generate_sales_report()
