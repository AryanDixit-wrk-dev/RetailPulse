select
    c.category_name,
    sum(f.quantity) as total_quantity,
    sum(f.total_sales) as total_sales,
    count(distinct f.order_id) as total_orders
from {{ ref('int_sales') }} f
join {{ source('retailpulse_warehouse', 'dim_category') }} c
    on f.category_key = c.category_key
group by c.category_name
order by total_sales desc