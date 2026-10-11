select
    run_id,
    pipeline_name,
    source_file,
    source_hash,
    status,
    started_at,
    completed_at,
    records_received,
    records_accepted,
    records_rejected,
    records_processed,
    error_message
from {{ source('retailpulse_warehouse', 'pipeline_runs') }}