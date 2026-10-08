import uuid
from db.connection import get_connection
from db.pipeline_runs import create_pipeline_run, complete_pipeline_run


def test_pipeline_run_lifecycle():
    conn = get_connection()
    source_hash = f"lifecycle-test-{uuid.uuid4()}"

    try:
        run_id = create_pipeline_run(
            conn,
            pipeline_name="test_pipeline",
            source_file="test.csv",
            source_hash=source_hash,
        )

        assert isinstance(run_id, int)

        complete_pipeline_run(
            conn,
            run_id=run_id,
            status="SUCCESS",
            records_processed=3,
        )

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    pipeline_name,
                    source_file,
                    source_hash,
                    status,
                    records_processed,
                    completed_at,
                    error_message
                FROM pipeline_runs
                WHERE run_id = %s
                """,
                (run_id,),
            )

            row = cursor.fetchone()

        assert row is not None
        assert row[0] == "test_pipeline"
        assert row[1] == "test.csv"
        assert row[2] == source_hash
        assert row[3] == "SUCCESS"
        assert row[4] == 3
        assert row[5] is not None
        assert row[6] is None

    finally:
        conn.close()
def test_duplicate_successful_batch_is_detected():
    conn = get_connection()
    source_hash = f"duplicate-test-{uuid.uuid4()}"

    try:
        run_id = create_pipeline_run(
            conn,
            pipeline_name="test_pipeline",
            source_file="test.csv",
            source_hash=source_hash,
        )

        complete_pipeline_run(
            conn,
            run_id=run_id,
            status="SUCCESS",
            records_processed=3,
        )

        from db.pipeline_runs import pipeline_run_exists

        assert pipeline_run_exists(
            conn,
            pipeline_name="test_pipeline",
            source_hash=source_hash,
        ) is True

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM pipeline_runs WHERE run_id = %s",
                (run_id,),
            )
        conn.commit()
        conn.close()
def test_duplicate_successful_batch_is_rejected():
    conn = get_connection()
    source_hash = f"race-test-{uuid.uuid4()}"

    try:
        first_run_id = create_pipeline_run(
            conn,
            pipeline_name="test_pipeline",
            source_file="test.csv",
            source_hash=source_hash,
        )

        complete_pipeline_run(
            conn,
            run_id=first_run_id,
            status="SUCCESS",
            records_processed=3,
        )

        second_run_id = create_pipeline_run(
            conn,
            pipeline_name="test_pipeline",
            source_file="test.csv",
            source_hash=source_hash,
        )

        try:
            complete_pipeline_run(
                conn,
                run_id=second_run_id,
                status="SUCCESS",
                records_processed=3,
            )
        except Exception:
            conn.rollback()
        else:
            raise AssertionError(
                "Duplicate successful batch should be rejected."
            )

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM pipeline_runs
                WHERE source_hash = %s
                """,
                (source_hash,),
            )
        conn.commit()
        conn.close()