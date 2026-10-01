import argparse
import logging

from ingestion.load_csv import load_csv
from validation.validate_sales import validate_sales_data
from validation.data_quality import (
    generate_quality_report,
    save_quality_report,
)
from db.connection import get_connection
from db.loaders.sales_loader import load_sales_to_database
from analytics.generate_report import generate_sales_report


logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run_sales_pipeline(file_path: str):

    logger.info("Starting sales pipeline")

    # 1. Extract
    df = load_csv(file_path)
    logger.info("Loaded %d records", len(df))

    # 2. Data quality
    quality_report = generate_quality_report(df)
    save_quality_report(quality_report)
    logger.info("Data quality report generated")

    # 3. Validate
    errors = validate_sales_data(df)

    if errors:
        logger.error("Validation failed")

        for error in errors:
            logger.error(error)

        return False

    logger.info("Validation passed")

    # 4. Load into PostgreSQL
    conn = get_connection()

    try:
        affected_rows = load_sales_to_database(df, conn)
        logger.info(
            "Database load completed. Affected rows: %d",
            affected_rows,
        )
    finally:
        conn.close()

    # 5. Generate reports
    generate_sales_report()
    logger.info("Reports generated successfully")

    logger.info("Pipeline completed successfully")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the RetailPulse sales pipeline."
    )

    parser.add_argument(
        "file_path",
        help="Path to the sales CSV file.",
    )

    args = parser.parse_args()

    success = run_sales_pipeline(args.file_path)

    if not success:
        raise SystemExit(1)