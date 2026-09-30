import logging

from ingestion.load_csv import load_csv
from validation.validate_sales import validate_sales_data


logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run_sales_pipeline(file_path: str):

    logger.info("Starting sales pipeline")

    # Extract
    df = load_csv(file_path)
    logger.info("Loaded %d records", len(df))

    # Validate
    errors = validate_sales_data(df)

    if errors:
        logger.error("Validation failed")

        for error in errors:
            logger.error(error)

        return False

    logger.info("Validation passed")
    logger.info("Pipeline completed successfully")

    return True


if __name__ == "__main__":
    run_sales_pipeline("data/raw/sample_sales.csv")