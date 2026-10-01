SELECT
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(quantity * price) AS total_sales,
    AVG(quantity * price) AS average_order_value
FROM sales;