select
    sum(total_sales) as total_sales,
    count(distinct order_id) as total_orders,
    sum(quantity) as total_quantity
from {{ ref('int_sales') }}