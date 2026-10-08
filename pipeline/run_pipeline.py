import argparse
import logging

from psycopg.errors import UniqueViolation

from ingestion.load_csv import load_csv
from contracts.sales_contract import validate_sales_schema
from validation.validate_sales import (
    validate_sales_data,
    split_valid_invalid_sales,
)
from db.loaders.quarantine_loader import load_quarantine_records
from validation.data_quality import (
    generate_quality_report,
    save_quality_report,
)
from transformation.sales_transform import transform_sales_data
from db.connection import get_connection
from db.pipeline_runs import (
    calculate_file_hash,
    pipeline_run_exists,
    create_pipeline_run,
    complete_pipeline_run,
    skip_pipeline_run,
)
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

    conn = get_connection()

    source_hash = calculate_file_hash(file_path)

    if pipeline_run_exists(
        conn,
        pipeline_name="sales_pipeline",
        source_hash=source_hash,
    ):
        logger.info(
            "Batch already processed successfully. Skipping: %s",
            file_path,
        )
        conn.close()
        return True

    run_id = create_pipeline_run(
        conn,
        pipeline_name="sales_pipeline",
        source_file=file_path,
        source_hash=source_hash,
    )

    try:
        # 1. Extract
        df = load_csv(file_path)
        logger.info("Loaded %d records", len(df))

        # 2. Data contract
        schema_errors = validate_sales_schema(df)

        if schema_errors:
            error_message = "; ".join(schema_errors)

            complete_pipeline_run(
                conn,
                run_id=run_id,
                status="FAILED",
                records_processed=0,
                error_message=error_message,
            )

            logger.error("Data contract validation failed")

            for error in schema_errors:
                logger.error(error)

            return False

        logger.info("Data contract validation passed")

        # 3. Data quality
        quality_report = generate_quality_report(df)
        save_quality_report(quality_report)
        logger.info("Data quality report generated")

        # 4. Business validation
        valid_rows, invalid_rows, rejection_reasons = split_valid_invalid_sales(df)

        logger.info(
            "Valid rows: %d, Invalid rows: %d",
            len(valid_rows),
            len(invalid_rows),
        )

        df = valid_rows 

        # 5. Transform
        df = transform_sales_data(df)
        logger.info("Sales data transformed")

        # 6. Load into PostgreSQL
        affected_rows = load_sales_to_database(
            df,
            conn,
            pipeline_run_id=run_id,
        )

        logger.info(
            "Database load completed. Affected rows: %d",
            affected_rows,
        )

        # 7. Generate reports
        generate_sales_report()
        logger.info("Reports generated successfully")

        # 8. Complete pipeline run
        try:
            complete_pipeline_run(
                conn,
                run_id=run_id,
                status="SUCCESS",
                records_processed=len(df),
            )
        except UniqueViolation:
            conn.rollback()

            skip_pipeline_run(
                conn,
                run_id=run_id,
                reason="Batch was already processed successfully.",
            )

            logger.info(
                "Batch was already processed by another pipeline run. "
                "Run skipped: %s",
                run_id,
            )

            return True

        logger.info("Pipeline completed successfully")
        return True

    except Exception as exc:
        logger.exception("Pipeline failed")

        complete_pipeline_run(
            conn,
            run_id=run_id,
            status="FAILED",
            records_processed=0,
            error_message=str(exc),
        )

        raise

    finally:
        conn.close()


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