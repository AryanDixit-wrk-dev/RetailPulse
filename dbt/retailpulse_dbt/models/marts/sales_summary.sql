select
    count(*) as total_orders,
    sum(quantity) as total_quantity,
    sum(total_sales) as total_sales,
    avg(total_sales) as average_order_value
from {{ ref('int_sales') }}