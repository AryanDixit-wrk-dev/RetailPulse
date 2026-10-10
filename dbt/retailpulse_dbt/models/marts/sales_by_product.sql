select
    p.product_name,
    sum(f.quantity) as total_quantity,
    sum(f.total_sales) as total_sales,
    count(distinct f.order_id) as total_orders
from {{ ref('int_sales') }} f
join {{ source('retailpulse_warehouse', 'dim_product') }} p
    on f.product_key = p.product_key
group by p.product_name
order by total_sales desc