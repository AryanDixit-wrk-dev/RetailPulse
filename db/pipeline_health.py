def get_recent_pipeline_runs(
    conn,
    limit: int = 10,
) -> list[dict]:
    """Return recent pipeline runs ordered by start time."""

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                run_id,
                pipeline_name,
                source_file,
                status,
                started_at,
                completed_at,
                records_received,
                records_accepted,
                records_rejected,
                records_processed,
                error_message
            FROM pipeline_runs
            ORDER BY started_at DESC
            LIMIT %s
            """,
            (limit,),
        )

        columns = [column.name for column in cursor.description]
        rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def get_pipeline_health(
    conn,
) -> dict:
    """Return a summary of the latest pipeline execution."""

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_runs,
                COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs,
                COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
                COUNT(*) FILTER (WHERE status = 'SKIPPED') AS skipped_runs,
                MAX(started_at) AS latest_run_at
            FROM pipeline_runs
            """
        )

        row = cursor.fetchone()

    return {
        "total_runs": row[0],
        "successful_runs": row[1],
        "failed_runs": row[2],
        "skipped_runs": row[3],
        "latest_run_at": row[4],
    }