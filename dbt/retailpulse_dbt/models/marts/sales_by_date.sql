select
    d.full_date,
    d.year as order_year,
    d.month as order_month,
    d.quarter as order_quarter,
    sum(f.quantity) as total_quantity,
    sum(f.total_sales) as total_sales,
    count(distinct f.order_id) as total_orders
from {{ ref('int_sales') }} f
join {{ source('retailpulse_warehouse', 'dim_date') }} d
    on f.date_key = d.date_key
group by
    d.full_date,
    d.year,
    d.month,
    d.quarter
order by d.full_date