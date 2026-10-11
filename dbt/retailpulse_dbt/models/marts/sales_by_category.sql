select
    category_key,
    sum(quantity) as total_quantity,
    sum(total_sales) as total_sales
from {{ ref('int_sales') }}
group by category_key