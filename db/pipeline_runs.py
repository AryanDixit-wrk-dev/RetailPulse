import hashlib
from datetime import datetime
from pathlib import Path


def calculate_file_hash(file_path: str) -> str:
    """Calculate the SHA-256 hash of a source file."""

    sha256 = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def pipeline_run_exists(
    conn,
    pipeline_name: str,
    source_hash: str,
) -> bool:
    """Check whether a successful run already exists for this batch."""

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pipeline_runs
            WHERE pipeline_name = %s
              AND source_hash = %s
              AND status = 'SUCCESS'
            LIMIT 1
            """,
            (pipeline_name, source_hash),
        )

        return cursor.fetchone() is not None


def create_pipeline_run(
    conn,
    pipeline_name: str,
    source_file: str,
    source_hash: str,
) -> int:
    """Create a pipeline run record and return its run ID."""

    started_at = datetime.now().astimezone()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO pipeline_runs (
                pipeline_name,
                source_file,
                source_hash,
                status,
                started_at
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING run_id
            """,
            (
                pipeline_name,
                source_file,
                source_hash,
                "RUNNING",
                started_at,
            ),
        )

        run_id = cursor.fetchone()[0]

    conn.commit()
    return run_id


def complete_pipeline_run(
    conn,
    run_id: int,
    status: str,
    records_received: int | None = None,
    records_accepted: int | None = None,
    records_rejected: int | None = None,
    records_processed: int | None = None,
    error_message: str | None = None,
):
    """Complete a pipeline run with its final status."""

    completed_at = datetime.now().astimezone()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE pipeline_runs
            SET
                completed_at = %s,
                status = %s,
                records_received = %s,
                records_accepted = %s,
                records_rejected = %s,
                records_processed = %s,
                error_message = %s
            WHERE run_id = %s
            """,
            (
                completed_at,
                status,
                records_received,
                records_accepted,
                records_rejected,
                records_processed,
                error_message,
                run_id,
            ),
        )

    conn.commit()


def skip_pipeline_run(
    conn,
    run_id: int,
    reason: str,
):
    """Mark a pipeline run as skipped."""

    completed_at = datetime.now().astimezone()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE pipeline_runs
            SET
                completed_at = %s,
                status = %s,
                error_message = %s
            WHERE run_id = %s
            """,
            (
                completed_at,
                "SKIPPED",
                reason,
                run_id,
            ),
        )

    conn.commit()