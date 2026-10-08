import json

import pandas as pd


def load_quarantine_records(
    df: pd.DataFrame,
    conn,
    pipeline_run_id: int,
    source_file: str,
    rejection_reason: str,
) -> int:
    """Load rejected sales records into the quarantine table."""

    inserted_rows = 0

    with conn.cursor() as cursor:
        for row in df.to_dict(orient="records"):
            cursor.execute(
                """
                INSERT INTO sales_quarantine (
                    pipeline_run_id,
                    source_file,
                    order_id,
                    raw_record,
                    rejection_reason
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    pipeline_run_id,
                    source_file,
                    row.get("order_id"),
                    json.dumps(row, default=str),
                    rejection_reason,
                ),
            )

            inserted_rows += 1

    conn.commit()

    return inserted_rows
