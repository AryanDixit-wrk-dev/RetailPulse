select
    order_id,
    date_key,
    product_key,
    category_key,
    quantity,
    unit_price,
    total_sales,
    pipeline_run_id
from {{ ref('stg_sales') }}