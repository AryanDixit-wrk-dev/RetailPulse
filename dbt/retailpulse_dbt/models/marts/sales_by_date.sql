select
    date_key,
    sum(quantity) as total_quantity,
    sum(total_sales) as total_sales,
    count(distinct order_id) as total_orders
from {{ ref('int_sales') }}
group by date_key