select
    order_id,
    product,
    category,
    quantity,
    price,
    order_date
from {{ source('retailpulse', 'sales') }}