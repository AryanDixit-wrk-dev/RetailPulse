select *
from {{ ref('stg_sales') }}
where unit_price <= 0