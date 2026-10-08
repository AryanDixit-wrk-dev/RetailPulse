CREATE TABLE IF NOT EXISTS sales (
    order_id INTEGER PRIMARY KEY,
    product TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    order_date DATE NOT NULL,
    pipeline_run_id BIGINT
);
ALTER TABLE sales
ADD COLUMN IF NOT EXISTS pipeline_run_id BIGINT;

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    source_file TEXT NOT NULL,
    source_hash TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    records_processed INTEGER,
    error_message TEXT
);

ALTER TABLE pipeline_runs
ADD COLUMN IF NOT EXISTS source_hash TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS uq_pipeline_runs_success_hash
ON pipeline_runs (pipeline_name, source_hash)
WHERE status = 'SUCCESS'
  AND source_hash IS NOT NULL;