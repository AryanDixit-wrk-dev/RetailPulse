import argparse
import time

from psycopg.errors import UniqueViolation

from analytics.generate_report import generate_sales_report
from contracts.sales_contract import validate_sales_schema
from db.connection import get_connection
from db.loaders.quarantine_loader import load_quarantine_records
from db.loaders.sales_loader import load_sales_to_database
from db.loaders.warehouse_loader import load_warehouse_data
from db.pipeline_runs import (
    calculate_file_hash,
    complete_pipeline_run,
    create_pipeline_run,
    pipeline_run_exists,
    skip_pipeline_run,
)
from ingestion.load_csv import load_csv
from transformation.sales_transform import transform_sales_data
from utils.logging_config import configure_logging
from validation.data_quality import (
    generate_quality_report,
    save_quality_report,
)
from validation.validate_sales import split_valid_invalid_sales


logger = configure_logging()


def run_sales_pipeline(file_path: str):
    start_time = time.perf_counter()

    logger.info("Starting sales pipeline: %s", file_path)

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

    logger.info("Created pipeline run: %d", run_id)

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
                records_received=len(df),
                records_accepted=0,
                records_rejected=len(df),
                records_processed=0,
                error_message=error_message,
            )

            logger.error(
                "Data contract validation failed for run %d",
                run_id,
            )

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
            "Validation completed. Valid rows: %d, Invalid rows: %d",
            len(valid_rows),
            len(invalid_rows),
        )

        df = valid_rows

        if not invalid_rows.empty:
            for reason in rejection_reasons.unique():
                rows = invalid_rows[rejection_reasons == reason]

                load_quarantine_records(
                    rows,
                    conn,
                    pipeline_run_id=run_id,
                    source_file=file_path,
                    rejection_reason=reason,
                )

                logger.warning(
                    "Quarantined %d rows. Reason: %s",
                    len(rows),
                    reason,
                )

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

        # 7. Load warehouse
        warehouse_rows = load_warehouse_data(
            df,
            conn,
            pipeline_run_id=run_id,
        )

        logger.info(
            "Warehouse load completed. Rows loaded: %d",
            warehouse_rows,
        )

        # 8. Generate reports
        generate_sales_report()
        logger.info("Reports generated successfully")

        # 9. Complete pipeline run
        try:
            complete_pipeline_run(
                conn,
                run_id=run_id,
                status="SUCCESS",
                records_received=len(df) + len(invalid_rows),
                records_accepted=len(df),
                records_rejected=len(invalid_rows),
                records_processed=len(df),
            )
        except UniqueViolation:
            conn.rollback()

            skip_pipeline_run(
                conn,
                run_id=run_id,
                reason="Batch was already processed successfully.",
            )

            duration = time.perf_counter() - start_time

            logger.info(
                "Batch was already processed by another pipeline run. "
                "Run skipped: %d, Duration: %.2f seconds",
                run_id,
                duration,
            )

            return True

        duration = time.perf_counter() - start_time

        logger.info(
            "Pipeline completed successfully. "
            "Run: %d, Received: %d, Accepted: %d, Rejected: %d, "
            "Processed: %d, Duration: %.2f seconds",
            run_id,
            len(df) + len(invalid_rows),
            len(df),
            len(invalid_rows),
            len(df),
            duration,
        )

        return True

    except Exception as exc:
        duration = time.perf_counter() - start_time

        logger.exception(
            "Pipeline failed. Run: %d, Duration: %.2f seconds",
            run_id,
            duration,
        )

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