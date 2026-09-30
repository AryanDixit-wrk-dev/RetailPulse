import json
from pathlib import Path

from db.connection import get_connection
from db.readers.sales_reader import read_sales_from_database
from analytics.sales_metrics import (
    calculate_sales_metrics,
    sales_by_product,
)


def generate_sales_report():
    """Generate sales summary and product-level reports."""

    conn = get_connection()

    try:
        sales_df = read_sales_from_database(conn)
    finally:
        conn.close()

    # Overall metrics
    metrics = calculate_sales_metrics(sales_df)

    summary_path = Path("reports/sales_summary.json")
    summary_path.write_text(
        json.dumps(metrics, indent=4),
        encoding="utf-8",
    )

    # Product-level metrics
    product_report = sales_by_product(sales_df)

    product_path = Path("reports/sales_by_product.csv")
    product_report.to_csv(product_path, index=False)

    print(f"Summary report generated: {summary_path}")
    print(f"Product report generated: {product_path}")


if __name__ == "__main__":
    generate_sales_report()