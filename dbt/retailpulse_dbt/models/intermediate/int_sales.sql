select
    order_id,
    product,
    category,
    quantity,
    price,
    order_date,
    quantity * price as total_sales
from {{ ref('stg_sales') }}