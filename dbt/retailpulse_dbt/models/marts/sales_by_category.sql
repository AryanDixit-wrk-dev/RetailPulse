select
    category,
    sum(quantity) as total_quantity,
    sum(total_sales) as total_sales,
    count(*) as total_orders
from {{ ref('int_sales') }}
group by category
order by total_sales desc