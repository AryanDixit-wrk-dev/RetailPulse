SELECT
    order_date,
    SUM(quantity) AS total_quantity,
    SUM(quantity * price) AS total_sales,
    COUNT(*) AS total_orders
FROM sales
GROUP BY order_date
ORDER BY order_date;