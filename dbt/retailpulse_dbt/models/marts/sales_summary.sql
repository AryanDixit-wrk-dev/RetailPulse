select
    count(distinct f.order_id) as total_orders,
    sum(f.quantity) as total_quantity,
    sum(f.total_sales) as total_sales,
    avg(f.total_sales) as average_order_value
from {{ ref('int_sales') }} f