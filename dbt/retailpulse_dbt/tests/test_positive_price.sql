select *
from {{ ref('stg_sales') }}
where price <= 0
