select *
from {{ ref('stg_sales') }}
where quantity <= 0
