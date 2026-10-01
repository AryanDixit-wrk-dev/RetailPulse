select
    order_date,
    sum(quantity) as total_quantity,
    sum(total_sales) as total_sales,
    count(*) as total_orders
from {{ ref('int_sales') }}
group by order_date
order by order_date